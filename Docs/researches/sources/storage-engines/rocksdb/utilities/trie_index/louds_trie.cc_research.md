# sources/storage-engines/rocksdb/utilities/trie_index/louds_trie.cc

## Purpose

`louds_trie.cc` implements the experimental RocksDB trie-index core declared in `louds_trie.h`: a fast succinct trie based on LOUDS with dense upper levels, sparse lower levels, optional sparse path-compression chains, packed block-handle arrays, and an optional sequence-number side table for same-user-key block runs. The implementation has two roles:

- `LoudsTrieBuilder` converts sorted separator keys and block handles into one serialized, flat, mostly zero-copy structure suitable for SST metadata storage.
- `LoudsTrie` and `LoudsTrieIterator` parse that structure and provide seek, forward scan, and reverse scan over separator leaves while reconstructing keys and returning block handles by leaf ordinal.

The format is self-contained: a fixed magic/version header, dense bitvectors, sparse labels and bitvectors, sparse child-position tables, chain metadata, handle arrays, and optionally seqno/overflow arrays.

## Important APIs, Types, And Functions

- `kTrieFormatVersion`, `kTrieMagic`, `kFlagSeqnoEncoding`: local serialization contract constants. `kTrieMagic` is `"TRIE"` and the seqno flag controls whether side-table parsing is required.
- `LoudsTrieBuilder::AddKey()`: appends a sorted separator key and primary block handle without seqno metadata.
- `LoudsTrieBuilder::AddKeyWithSeqno()`: appends a separator plus its seqno tag and count of blocks sharing that separator.
- `LoudsTrieBuilder::AddOverflowBlock()`: appends overflow block handle/seqno entries for the most recent duplicate-separator run. It explicitly tolerates `seqno == 0`, which matters for bottommost compaction.
- `LoudsTrieBuilder::ComputeCutoffLevel()`: estimates dense versus sparse cost per level from sorted-key LCPs and returns the first level where sparse is cheaper.
- `LoudsTrieBuilder::Finish()`: computes `max_depth_`, selects the cutoff, builds per-level trie arrays directly from sorted keys, emits LOUDS-dense/sparse structures, reorders handles and seqno metadata into BFS leaf order, and calls `SerializeAll()`.
- `LoudsTrieBuilder::SerializeAll()`: writes the complete on-disk/in-memory byte format, including bitvectors, sparse child lookup tables, chain metadata, handle arrays, and seqno side table.
- `LoudsTrie::InitFromData()`: validates and binds a serialized buffer into `Bitvector` and raw-array pointers, copying into `aligned_copy_` only when the input pointer is not 8-byte aligned.
- `LoudsTrie::GetHandle()`: returns packed offset/size for a leaf index.
- Dense iterator helpers: `DenseSeekLabel()`, `DenseChildNodeNumFromRank()`, `DenseLeafIndexFromRank*()`, `DensePrefixKeyLeafIndex()`.
- Sparse iterator helpers: `SparseSeekLabel()`, `SparseChildNodeNum()`, `SparseLeafIndex*()`, `SparsePrefixKeyLeafIndex()`, `SparseNodeStartPos()`, `SparseNodeEndPos()`.
- Traversal methods: `SeekToFirst()`, `SeekImpl<kHasChains>()`, `Next()`, `Advance()`, `SeekToLast()`, `Prev()`, `Retreat()`, `DescendToLeftmostLeaf()`, and `DescendToRightmostLeaf()`.

## Builder Control Flow

`Finish()` begins with the empty-trie case, writing a valid serialized structure with zero keys, zero depth, and no dense/sparse nodes. Non-empty builds first compute `max_depth_` and a dense/sparse cutoff from per-level node and label estimates.

The main trie-construction pass avoids building heap-allocated trie nodes. It defines local `PerLevelData` vectors for each depth:

- `labels`, `has_child`, and `leaf_handle` store per-label data.
- `is_prefix`, `prefix_handle`, and `node_label_start` store per-node data.

For every sorted key, it computes the LCP with the previous key. If the previous key had ended at a label that now becomes an internal branch, `Finish()` retroactively flips that last label from leaf to internal, moves the old handle into a newly created prefix-key child node, and clears the label leaf handle. It then adds labels from the LCP point through the key end, creating new nodes for deeper levels and associating the input key index with terminal labels.

The second phase walks per-level nodes in BFS order:

- Dense levels append one `d_is_prefix_key_` bit per node, a 256-bit label bitmap per node, one `d_has_child_` bit per present label, and dense leaf counts.
- Sparse levels append labels to `s_labels_`, `s_has_child_`, `s_louds_`, and `s_is_prefix_key_`.
- Prefix-key handles are emitted before child-label leaf handles so leaf ordinal formulas match traversal order.
- `dense_child_count_` records internal children at the final dense level that become sparse roots; if the trie is all sparse (`cutoff_level_ == 0`), it is set to 1 for the root sparse node.

Handles, seqnos, block counts, and overflow arrays are reordered from input/key order into BFS leaf order as leaves are emitted. This is critical because separator key order and BFS leaf order can differ when keys have different lengths or prefix relationships.

## Serialization Layout And Persistence Behavior

`SerializeAll()` writes a stable flat representation:

1. Header: magic, version, `num_keys`, `cutoff_level`, `max_depth`, `dense_leaf_count`, `dense_node_count`, `dense_child_count`, flags, and reserved padding. The header is 56 bytes and keeps later arrays 8-byte aligned.
2. Dense bitvectors: `d_labels_`, `d_has_child_`, `d_is_prefix_key_`, each encoded through `Bitvector::EncodeTo()`.
3. Sparse labels: `uint64_t` size, raw byte label data, then 8-byte padding.
4. Sparse bitvectors: `s_has_child_`, `s_louds_`, `s_is_prefix_key_`.
5. Sparse child-position lookup tables: `num_internal`, then `uint32_t` child start positions and `uint32_t` child end positions, padded separately. These let sparse traversal use rank plus array lookup instead of repeated select operations.
6. Path-compression chain metadata: `num_chains`, optional bitmap, compact suffix offsets, chain lengths, chain-end child indexes, and suffix bytes.
7. Primary block handle arrays: `uint32_t[num_keys]` offsets and `uint32_t[num_keys]` sizes, padded to 8-byte boundaries.
8. Optional seqno side table: overflow count, per-leaf `uint64_t` seqnos, per-leaf `uint32_t` block counts, overflow offsets, overflow sizes, and overflow seqnos.

The trie itself is immutable after serialization. `LoudsTrie::InitFromData()` normally points directly into the caller-owned buffer; if the buffer address is not 8-byte aligned, it copies into `aligned_copy_` and all pointers reference that owned buffer. Persistence therefore depends on the caller keeping the serialized data alive for the lifetime of the trie unless `aligned_copy_` is populated.

## Deserialization And Validation

`InitFromData()` treats serialized input as untrusted. It validates:

- Minimum header size, magic, and format version.
- `num_keys_ <= 1 << 30` to avoid later size arithmetic overflow.
- `max_depth_ <= 65536` to prevent iterator buffer allocation overflow.
- Dense bitvector dimensions: dense labels must equal `dense_node_count_ * 256`, dense has-child bits must equal dense label ones, and dense prefix bits must equal dense node count.
- `dense_leaf_count_ <= num_keys_`.
- Sparse label payload bounds and padding.
- Sparse bitvector sizes equal sparse label count.
- Child-position table count and each start/end range.
- Chain count sections, chain end indexes, and suffix offset/length ranges.
- Handle array truncation and alignment.
- Seqno side-table truncation, alignment, nonzero per-leaf block counts, overflow count limit, and prefix-sum consistency with `num_overflow_blocks_`.

It returns `Status::Corruption()` on malformed input and `Status::OK()` after successful binding. One notable detail: after reading `overflow_seqnos_`, the code intentionally does not advance `p`/`remaining` because no later section is parsed.

## Iterator Control Flow

`LoudsTrieIterator` reconstructs keys by maintaining a `path_` stack of dense bit positions or sparse label positions and a `key_buf_` sized to `MaxDepth()+1`.

Forward traversal:

- `SeekToFirst()` resets state and descends from root to the leftmost leaf, checking prefix keys before children.
- `Seek()` dispatches to `SeekImpl<true>` if chain metadata exists, otherwise `SeekImpl<false>`, keeping chain code out of the no-chain instruction path.
- Dense seek uses a 256-bit node bitmap lookup and `NextSetBit()` to land on exact or next-greater labels.
- Sparse seek uses a fanout-1 fast path, linear scan for fanout <= 16, and `std::lower_bound` for larger nodes.
- If a target byte lands on a greater label, traversal descends to that subtree's leftmost leaf. If a trie leaf is a proper prefix of the target, it advances to the next leaf.
- When sparse chains are enabled and a child index has a chain bit, `SeekImpl` compares the remaining target bytes against the stored suffix with `memcmp`, pushes any skipped chain positions needed for key reconstruction/backtracking, and handles full match, mismatch, target-shorter, chain-ending-at-leaf, and chain-ending-at-internal cases.
- After the target is consumed, `SeekImpl` checks whether the current node is a prefix key, otherwise descends to the leftmost leaf below it.
- `Next()` has a special prefix-key case: a prefix leaf is followed by the leftmost child leaf without re-returning the prefix; otherwise it calls `Advance()`.
- `Advance()` backtracks until it finds a next sibling in the same dense bitmap or sparse node, replaces the top stack entry in place, updates the last key byte, and descends leftmost if the sibling is internal.

Reverse traversal:

- `SeekToLast()` descends to the rightmost leaf, deliberately skipping prefix-key checks because prefix keys are smallest within a node and should appear after children during reverse iteration.
- `Prev()` clears the prefix flag and calls `Retreat()`.
- `Retreat()` finds previous siblings or, when none exist, returns the node's prefix key before popping further. It mirrors `Advance()` while respecting prefix-key ordering.

## Leaf Ordinals And Block Handles

The implementation relies on rank formulas that convert traversal positions to BFS leaf ordinals. Dense leaf ordinals count non-internal dense labels and prefix keys before or at the current dense node. Sparse leaf ordinals offset by `dense_leaf_count_`, count non-internal sparse labels, and add sparse prefix keys when present. Prefix-key leaf ordinals count labels before the node plus prefix keys before the node.

`GetHandle()` maps those leaf ordinals to packed `uint32_t` offset/size arrays. Assertions assume indexes are in bounds after successful traversal.

## Dependencies And Integration Points

Direct dependencies are `louds_trie.h`, `<algorithm>`, `<cassert>`, `<cstring>`, `<limits>`, `<utility>`, and RocksDB `util/coding.h` for fixed-width serialization. The implementation depends on `Bitvector` and `BitvectorBuilder` for rank/select/next/previous set-bit operations and encoding.

The main integration point is `utilities/trie_index/trie_index_factory.cc`. `TrieIndexBuilder` buffers SST index entries, forces seqno encoding, deduplicates consecutive equal separators into primary plus overflow blocks, and feeds `LoudsTrieBuilder`. `TrieIndexIterator` wraps `LoudsTrieIterator` for the user-defined index interface, uses trie keys as user-key separators, and applies the seqno side table for same-user-key and last-block correction.

The file also depends on sorted input keys. The builder comments require sorted keys, but the implementation primarily asserts local structural invariants rather than sorting or returning an error for unsorted input.

## State And Memory Behavior

Builder state is mutable and accumulates all keys, handles, seqno fields, overflow blocks, bitvector builders, sparse labels, counts, and the final `serialized_data_` string. During `Finish()`, input handles and optional seqno vectors are replaced with BFS-ordered vectors.

Reader state is immutable after `InitFromData()`. It stores raw pointers into serialized memory for labels, handles, seqno arrays, and chain suffixes, plus owned vectors for child position tables, chain compact arrays, overflow bases, and optional aligned copy. `ApproximateAuxMemoryUsage()` in the header accounts only for sparse child start/end vectors.

Iterator state is transient: `valid_`, `leaf_index_`, `key_buf_`, `key_len_`, `path_`, and `is_at_prefix_key_`. Iterator methods mutate this state aggressively for hot-path traversal and are not thread-safe.

## Risks And Edge Cases

- Serialization compatibility is versioned but not negotiated beyond exact `kTrieFormatVersion == 1`.
- Primary handle offsets/sizes are asserted to fit in `uint32_t`; release builds still cast, so SST/file-size assumptions matter.
- Builder input order is trusted. Unsorted keys could produce malformed logical ordering without a clean error path.
- Many correctness properties depend on BFS handle reordering matching leaf ordinal formulas, especially for prefix keys and duplicate separator runs.
- Path-compression seek has many branchy cases; chain metadata validation prevents OOB reads, but logical ordering regressions are easy if chain detection and `SeekImpl` diverge.
- `LoudsTrie` move safety relies on `std::string` heap-buffer move preserving `aligned_copy_` pointer addresses; the header documents why this is expected, but the assumption is important for moved tries initialized from misaligned data.
- `InitFromData()` allows trailing bytes after the parsed structure because it does not require `remaining == 0`. This can be useful for embedded formats but means corruption checks focus on truncation and internal consistency rather than exact byte exhaustion.
- `AddOverflowBlock()` does not itself check that it is called exactly `block_count - 1` times for the most recent key; consistency is asserted/reconciled during finish/serialization assumptions and validated by reader prefix sums.

## Test Signals

Direct tests live in `sources/storage-engines/rocksdb/utilities/trie_index/trie_index_test.cc` under `LoudsTrieTest`.

Covered signals include:

- `TrieTopologyVariants`, `SingleKey`, `MultipleKeys`, `SharedPrefixKeys`, prefix-key seek tests, and binary key cases validate trie construction and key reconstruction across varied topologies.
- `HandleRoundTrip`, `PrefixKeyHandleReorderVerification`, and `LeafIndex` validate BFS leaf order and handle mapping.
- `IteratorSeekExact`, `IteratorSeekBetweenKeys`, `IteratorNext`, `SeekBetweenAllPairs`, `EmptyTargetSeek`, reseek tests, and invalid-iterator tests cover forward seeking and scanning.
- `SeekToLast`/`Prev` related tests in the same suite cover reverse traversal behavior.
- `InitFromDataCorruption`, `InitFromDataMaxDepthCorruption`, `InitFromDataUnsupportedVersion`, `InitFromDataProgressiveTruncation`, and `InitFromDataProgressiveTruncationWithChains` cover deserialization hardening.
- `SerializeDeserializeRoundTripMisalignedData`, `MoveConstructor`, and `MoveAssignment` cover alignment-copy and move semantics.
- `SparseBinarySearchPath`, `CutoffLevelAndMaxDepthAndHasChains`, `ChainSeekVariousTargets`, and `ChainSeekEndAtLeaf` exercise sparse binary search and chain-seek paths.
- Higher-level DB/SST integration tests in `trie_index_test.cc` and `trie_index_db_test.cc` exercise the factory and UDI integration over real RocksDB operations.
