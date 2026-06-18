# sources/storage-engines/rocksdb/utilities/trie_index/louds_trie.h

## Purpose

`louds_trie.h` declares the experimental LOUDS-based trie index used by RocksDB's trie-index utility. The header is both an API contract and a design document: it explains the hybrid LOUDS-Dense/LOUDS-Sparse layout, immutable serialized representation, BFS leaf ordinal formulas, block-handle mapping, key reconstruction, sparse child lookup tables, path-compression metadata, and optional sequence-number side-table support.

The public surface is intentionally small:

- Build a serialized trie from sorted separator keys with `LoudsTrieBuilder`.
- Initialize an immutable `LoudsTrie` from serialized bytes.
- Traverse leaves with `LoudsTrieIterator`.

## Important APIs And Types

- `TrieBlockHandle`: local offset/size pair for data block locations. It mirrors the user-defined index block handle shape while avoiding heavier header dependencies.
- `LoudsTrieBuilder`:
  - `AddKey(const Slice&, const TrieBlockHandle&)` records a separator and handle.
  - `AddKeyWithSeqno(const Slice&, const TrieBlockHandle&, uint64_t seqno, uint32_t block_count)` records a separator plus side-table metadata.
  - `AddOverflowBlock(const TrieBlockHandle&, uint64_t seqno)` records additional same-separator blocks after an `AddKeyWithSeqno()` run head.
  - `SetHasSeqnoEncoding(bool)` controls whether the serialized output includes seqno/overflow metadata.
  - `Finish()` finalizes the serialized byte representation.
  - `GetSerializedData()` exposes the built buffer as a `Slice`.
- `LoudsTrie`:
  - `InitFromData(const Slice&)` parses serialized bytes and binds internal pointers.
  - `NumKeys()`, `CutoffLevel()`, `MaxDepth()`, and `HasSeqnoEncoding()` expose header metadata.
  - `GetHandle(uint64_t)` maps leaf ordinal to primary block handle.
  - `HasChains()` reports whether sparse path-compression chains are present.
  - `ApproximateAuxMemoryUsage()` reports child-position table vector memory.
  - Seqno accessors expose per-leaf seqno, per-leaf block count, overflow base, overflow handle, and overflow seqno for `TrieIndexIterator`.
- `LoudsTrieIterator`:
  - `SeekToFirst()`, `SeekToLast()`, `Seek(const Slice&)`, `Next()`, and `Prev()` navigate sorted separator leaves.
  - `Valid()`, `Key()`, `LeafIndex()`, and `Value()` expose the current entry.

## Builder State Contract

The builder stores input keys and handles in `keys_` and `handles_`. When seqno encoding is enabled, it also stores:

- `seqnos_`: one tag per separator.
- `block_counts_`: number of consecutive data blocks sharing each separator.
- `overflow_handles_` and `overflow_seqnos_`: metadata for extra blocks in duplicate-separator runs.

The trie-building fields describe the serialized structure before encoding:

- `cutoff_level_` splits dense and sparse levels.
- `max_depth_` is the longest separator length.
- `d_labels_`, `d_has_child_`, `d_is_prefix_key_` are dense bitvector builders.
- `s_labels_`, `s_has_child_`, `s_louds_`, `s_is_prefix_key_` are sparse arrays/builders.
- `dense_leaf_count_`, `dense_node_count_`, and `dense_child_count_` are persisted counts used by reader formulas.
- `has_seqno_encoding_` is serialized into the header flags.
- `serialized_data_` owns the final bytes returned by `GetSerializedData()`.

The comments specify that keys must be added in sorted ascending order according to the SST comparator. `Finish()` is the transition point from mutable builder state to immutable serialized output.

## Reader State And Persistence Contract

`LoudsTrie` is a non-copyable, movable view over serialized data. It contains `Bitvector` members and raw pointers, so copying is disabled to avoid dangling or aliased pointer hazards. Moving is defaulted; the header documents the expected safety for `aligned_copy_` when data had to be copied due to unaligned input.

Core persisted metadata includes:

- `num_keys_`, `cutoff_level_`, `max_depth_`, `has_seqno_encoding_`.
- `dense_leaf_count_`, `dense_node_count_`, `dense_child_count_`.
- Dense bitvectors and sparse labels/bitvectors.
- Sparse child start/end vectors for select-free traversal.
- Sparse chain bitmap, suffix offsets, suffix lengths, chain end indexes, and suffix blob pointer.
- Packed primary block-handle arrays.
- Optional seqno side-table pointers and `overflow_base_` prefix-sum vector.
- `aligned_copy_`, used only when serialized input was not sufficiently aligned.

The trie does not generally own caller-supplied serialized data. Callers must preserve the backing bytes for as long as the `LoudsTrie` lives unless `InitFromData()` populated `aligned_copy_`.

## Iterator State And Control Flow Contract

`LoudsTrieIterator` is declared as the performance-critical traversal layer. It keeps:

- A `LevelPos` stack (`path_`) with dense positions encoded by setting bit 63 and sparse positions as raw label indexes.
- `key_buf_`, `key_len_`, and `key_cap_` for reconstructed separator keys.
- `leaf_index_` for mapping to handle arrays and seqno side tables.
- `is_at_prefix_key_` for keys that terminate at internal nodes.
- `has_chains_`, selected at construction, so `Seek()` dispatches to `SeekImpl<true>` or `SeekImpl<false>`.

The private helpers divide into dense helpers, sparse helpers, and traversal helpers. Dense traversal uses 256-bit label bitmaps and rank arithmetic. Sparse traversal uses sorted labels, `s_louds_` node boundaries, `s_has_child_` ranks, and child start/end lookup vectors. Prefix keys are explicitly represented by per-node prefix bitvectors rather than labels.

The iterator reconstructs one key byte per traversed label. For dense labels that byte is `pos % 256`; for sparse labels it is `s_labels_[pos]`. Prefix-key leaves have no additional terminal edge entry, so the prefix flag and path length rules matter for correct `Next()` and `Prev()` behavior.

## Dependencies And Integration Points

The header depends on:

- RocksDB public-ish primitives: `rocksdb/slice.h`, `rocksdb/status.h`.
- RocksDB utilities: `util/autovector.h` and `utilities/trie_index/bitvector.h`.
- C++ standard library headers for fixed-width types, memory ownership, strings, and vectors.

`LoudsTrieIterator` is a friend of `LoudsTrie` so it can directly access bitvectors and raw arrays without accessor overhead. The higher-level integration is through `trie_index_factory.h/.cc`, where `TrieIndexBuilder` owns a `LoudsTrieBuilder`, `TrieIndexIterator` wraps a `LoudsTrieIterator`, and `TrieIndexReader` owns or references a deserialized `LoudsTrie`.

## State, Encoding, And Leaf Ordering Notes

The header documents the main LOUDS formulas and ordering assumptions:

- Dense levels use 256-bit bitmaps per node for labels, plus a has-child bit per present label and a prefix-key bit per node.
- Sparse levels store byte labels plus `has_child`, `louds`, and prefix-key bitvectors.
- Dense leaf ordinals count dense label leaves and prefix keys with rank formulas.
- Sparse leaf ordinals add `dense_leaf_count_` and count sparse label leaves plus sparse prefix keys.
- Block handles are stored by BFS leaf ordinal rather than lexicographic input index, because BFS leaf order can differ when prefix keys are present.
- `dense_child_count_` offsets sparse node numbering for nodes that are roots of the sparse region.

Seqno side-table comments describe the contract used by the higher-level iterator: non-boundary leaves store zero as a sentinel, same-user-key boundaries and last-block leaves store real packed tags, and overflow arrays are addressed through a per-leaf prefix sum.

## Risks And Edge Cases

- `GetSerializedData()` is only valid after `Finish()` and returns a slice into `serialized_data_`; consumers must not outlive the builder/string unless they copy or initialize a trie while the bytes remain alive.
- The builder API relies on sorted input and correct `AddOverflowBlock()` sequencing after `AddKeyWithSeqno()` with `block_count > 1`.
- Public seqno accessors are assert-guarded, not status-returning; callers must check `HasSeqnoEncoding()` and keep indexes in range.
- The packed `LevelPos` representation assumes positions never use bit 63.
- Iterator key buffer safety depends on `max_depth_` validation in `InitFromData()` and the implementation using `AppendKeySlot()` for all appends.
- `LoudsTrie` move behavior is supported, but iterators hold raw `const LoudsTrie*`; any iterator must be recreated after moving the trie object.
- `ApproximateAuxMemoryUsage()` does not count serialized data, chain compact vectors, suffix data, or overflow-base memory, so it is a narrow auxiliary-memory estimate.

## Test Signals

The header's declared behavior is exercised by `utilities/trie_index/trie_index_test.cc`:

- Builder and iterator basics: empty trie, single key, multiple keys, shared prefixes, binary keys, full scans, seeks, and next iteration.
- Prefix-key behavior: prefix handle reorder verification and seeks around prefix keys.
- Reverse traversal: `SeekToLast()` and `Prev()` tests validate bidirectional API declarations.
- Reader lifetime/alignment/move behavior: serialize/deserialize, misaligned data, move constructor, and move assignment tests.
- Accessor behavior: `CutoffLevel()`, `MaxDepth()`, `HasChains()`, `LeafIndex()`, and `ApproximateAuxMemoryUsage()`.
- Corruption handling: bad magic, unsupported version, excessive max depth, progressive truncation, and chain truncation.
- Chain-specific behavior: chain metadata presence and seek targets that exercise full matches, mismatches, shorter targets, and chains ending at leaves.

The factory and DB/SST tests provide integration coverage for use through RocksDB's user-defined index path and seqno-aware block selection.
