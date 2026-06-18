# Research: sources/storage-engines/rocksdb/utilities/trie_index/trie_index_test.cc

## Purpose

This file is the primary GoogleTest coverage for RocksDB's experimental/user-defined trie index implementation under `utilities/trie_index`. It tests the low-level succinct data structures (`Bitvector`, `EliasFano`), the serialized `LoudsTrie` builder/reader/iterator, the `TrieIndexFactory` implementation of RocksDB's user-defined index API, end-to-end SST integration through block-based tables and `SstFileWriter`/`SstFileReader`, and a benchmark-style comparison against RocksDB's native `IndexBlockIter`.

The tests are especially focused on correctness at separator boundaries: bytewise trie ordering, prefix keys, dense/sparse trie transitions, path-compression chains, serialized data corruption, iterator invalidation/reseek behavior, multi-scan upper-bound checks, and same-user-key block boundaries where sequence numbers and value-type tags must be used to choose the same block that RocksDB's normal internal-key index would choose.

## Important APIs, Types, And Functions

- `SeekCtx(SequenceNumber)` and `EntryCtx(last_seq, first_seq)` are local helpers that convert readable sequence numbers into RocksDB's packed internal-key tag format. They feed `UserDefinedIndexIterator::SeekContext` and `UserDefinedIndexBuilder::IndexEntryContext`.
- `BitvectorTest` covers `BitvectorBuilder::Append`, `AppendMultiple`, `AppendWord`, `Reserve`, `BuildFrom`, and `Bitvector` APIs such as `GetBit`, `Rank1`, `Rank0`, `FindNthOneBit`, `FindNthZeroBit`, `NextSetBit`, `DistanceToNextSetBit`, `EncodeTo`, `InitFromData`, `SerializedSize`, move construction, and move assignment.
- `EliasFanoTest` covers `EliasFano::BuildFrom`, `Access`, `Count`, `Universe`, `EncodeTo`, `InitFromData`, `SerializedSize`, and move operations for monotone integer sequences used by trie/block-handle metadata compression.
- `LoudsTrieTest::BuiltTrie` owns a `LoudsTrieBuilder`, deserialized `LoudsTrie`, and `LoudsTrieIterator`; it has a custom move constructor because the iterator stores a raw pointer to the trie.
- `BuildTrieFromKeys`, `VerifyFullScan`, and `VerifyTrieIteration` are reusable trie fixtures that build sorted key sets with deterministic `TrieBlockHandle` offsets, then assert seek/scan/key reconstruction behavior.
- `TrieIndexFactoryTest::TestBlock` describes one data-block boundary with `last_key`, optional `next_key`, block handle, last sequence, and first sequence in the next block. `BuildTrieAndGetIterator` builds a full `UserDefinedIndexBuilder`/`Reader`/`Iterator` context from these blocks.
- `AssertSeekOffset` and `AssertFullForwardScan` are central assertions for user-defined index seek and next semantics. They validate both `IterateResult` status and the selected block offset.
- `TrieIndexSSTTest` integrates `TrieIndexFactory` with `BlockBasedTableOptions::user_defined_index_factory`, `SstFileWriter`, and `SstFileReader`.
- `TrieSeekBenchmark` creates synthetic trie and native index-block representations to compare seek cost against `IndexBlockIter`; it prints diagnostic timing to stderr but still runs as a test.

## Control Flow

The file starts at the smallest serialized primitives and moves outward. `BitvectorTest` builds bit patterns directly, materializes `Bitvector`s, checks rank/select/navigation invariants, then corrupts or truncates serialized buffers to verify defensive parsing. `EliasFanoTest` follows the same pattern for monotone offsets: empty/single/large/dense/constant distributions, serialization round trips, truncation, bad `low_bits`, and move behavior.

`LoudsTrieTest` then composes those primitives into trie behavior. The fixture adds sorted keys to `LoudsTrieBuilder`, calls `Finish`, initializes `LoudsTrie` from the builder's serialized slice, and uses `LoudsTrieIterator` for seeks and scans. The topology test table covers binary keys, all single-byte values, deep chains, high fanout, prefix-key chains, dense/sparse boundaries, mixed key lengths, long shared prefixes, and larger deterministic sets. Additional tests stress random key sets, exact/inexact seek, empty target seek, seek before/after all keys, repeated descending seeks, full-scan then reseek, empty trie iteration, key reconstruction, leaf-index accounting, sparse binary search, and path-compression chain comparisons.

The deserialization tests deliberately mutate or truncate trie headers and payloads. They check short data, wrong magic, unsupported version, excessive `max_depth`, progressive truncation with and without chains, misaligned input buffers, move construction/assignment, and auxiliary memory accounting. These tests exercise the reader's zero-copy design and pointer reseating logic after moves.

`TrieIndexFactoryTest` exercises the RocksDB user-defined index contract. It builds index entries the way a table builder would: last key, next first key when present, block handle, and sequence-tag context. It then verifies builder creation, reader creation, iterator creation, factory name, empty indexes, double `Finish` rejection, null comparator defaulting, non-bytewise comparator rejection, corrupted reader input, `OnKeyAdded` no-op behavior, approximate memory usage, and scan-bound preparation. Bounds tests verify that the UDI iterator returns `kInbound`, `kOutOfBound`, or `kUnknown` conservatively because separator keys are block upper bounds, not first keys in blocks.

The middle and later `TrieIndexFactoryTest` sections are a detailed same-user-key boundary suite. They build block layouts where multiple adjacent data blocks contain the same user key at different sequence numbers, so the index must use packed tags, overflow runs, and post-seek correction to mimic internal-key ordering. Tests cover large overflow runs, mixed and adjacent runs, zero-sequence bottommost-compaction cases, last-block real tags, non-boundary separators with sentinel tags, full tag comparisons for same sequence but different value types, all-`0xff` separator edge cases, randomized layouts, overflow BFS reordering, reverse iteration, `SeekToFirst`/`SeekToLast`, `Prev` inside overflow runs, and exhaustion followed by forward scanning through later overflow runs.

The SST integration tests write real SST files. They first prove native index reading still works because the UDI is stored alongside the normal index, then read with `ReadOptions::table_index_factory` set to the trie factory. They cover normal scans, point seeks, upper bounds, very small SSTs, mixed Put/Delete/Merge/SingleDelete-like internal key types, large mixed-type SSTs with many data blocks, and the compression-dictionary buffered replay path where `OnKeyAdded` must preserve first internal-key state for all operation types.

The benchmark test constructs a trie from fixed-width separator keys and a native index block using `BlockBuilder`, `IndexValue`, `Block`, and `IndexBlockIter`. For each key-count scale it generates random internal-key seeks, measures the production-like trie path (`ParseInternalKey`, user-key trie seek, key materialization, block-handle lookup) and the native index-block path (`IndexBlockIter::Seek`, `value`), and prints nanoseconds per operation and relative winner.

## State And Persistence Behavior

The test file itself has no persistent production state, but it validates many serialized states:

- `Bitvector` stores a header, packed words, rank lookup tables, and select hints. Tests verify `SerializedSize`, byte-for-byte consumption, non-aligned logical bit counts, out-of-range select behavior, and corruption on impossible headers or truncated auxiliary tables.
- `EliasFano` stores count/universe/low-bit metadata, low words, and a high bitvector. Tests validate empty and large sequences, access after deserialization, corrupted `low_bits`, truncated low-word/high-bitvector sections, and move safety when initialized from external serialized memory.
- `LoudsTrieBuilder` serializes a trie header, dense and sparse structures, block-handle arrays, path-compression chains, and auxiliary lookup data. Tests validate zero-copy initialization, misaligned buffer handling, maximum depth validation, unsupported versions, progressive truncation rejection, and `ApproximateAuxMemoryUsage`.
- `TrieIndexFactory` serializes user-defined index contents into `Slice index_contents` owned by the builder. The reader and iterator depend on that memory remaining alive, which is why helper contexts own builder, reader, and iterator together.
- SST integration writes temporary SST files under `test::PerThreadDBPath("trie_index_sst_test.sst")`; `TearDown` deletes the file through `Env::Default()->DeleteFile`.

## Dependencies And Integration Points

The tests depend on RocksDB core test infrastructure (`test_util/testharness.h`, `test_util/testutil.h`, `port/port.h`), core key-format helpers (`db/dbformat.h`, `PackSequenceAndType`, `InternalKey`, `ParsedInternalKey`, `AppendInternalKeyFooter`, `ParseInternalKey`), table infrastructure (`BlockBuilder`, `Block`, `IndexBlockIter`, `IndexValue`, `TableBuilder`, `BlockBasedTableOptions`, `NewBlockBasedTableFactory`), SST tools (`SstFileWriter`, `SstFileReader`), and trie-index components (`bitvector.h`, `louds_trie.h`, `trie_index_factory.h`).

Integration with RocksDB's block-based table stack is explicit. The trie factory is installed as `BlockBasedTableOptions::user_defined_index_factory`, then activated for reads through `ReadOptions::table_index_factory`. The tests also validate `UserDefinedIndexIteratorWrapper`, the adapter that exposes trie UDI results as internal keys to the block-based table iterator.

The file uses `MergeOperators::CreateStringAppendOperator()` to make Merge entries readable in SST tests and `GetSupportedDictCompressions()` plus compression dictionary options to trigger table-builder buffered mode.

## Risks And Edge Cases

- Many trie structures use zero-copy slices into serialized builder output. Tests maintain owner lifetimes carefully; future helper changes that return iterators without owning the serialized buffer can create dangling pointers.
- `LoudsTrieIterator` stores raw trie pointers, so moving a fixture requires rebuilding the iterator. The custom `BuiltTrie` move constructor documents and tests this risk.
- Sequence-number selection is subtle because RocksDB internal keys order higher packed tags before lower tags for the same user key. Tests verify that correction is only applied when target and separator user keys are equal; applying seqno logic to smaller user keys would skip valid blocks.
- Non-boundary shortened separators use tag `0` as a sentinel. Tests cover cases where separator shortening fails and confirm real sequence-number seeks do not advance incorrectly.
- Overflow runs have both key-sorted and BFS leaf-order dimensions. The `OverflowBfsReordering` test is a targeted guard against associating overflow block metadata with the wrong trie leaf.
- Bounds checks are intentionally conservative because separator keys are not first-in-block keys. Returning `kOutOfBound` too early can drop blocks that contain in-range data; returning `kUnknown` on SST exhaustion is necessary because another SST may still contain in-bound keys.
- Last block behavior differs from intermediate shortened separators because the last block stores its actual last key/tag. Tests ensure real-seqno seeks on the last separator match native index behavior.
- Compression dictionary buffered mode replays previously buffered data blocks. If UDI `OnKeyAdded` ignores non-Put internal value types, the table builder can assert or build an incomplete index.
- Randomized tests use time-derived seeds and print them through `SCOPED_TRACE`; failures require capturing the seed from test output for reproduction.

## Test Signals

This file is itself the test signal for the trie index feature. Strong signals include:

- Primitive invariants: rank/select correctness, select out-of-range sentinels, builder reserve/no-op append behavior, serialization size equality, and corruption on malformed bitvector/Elias-Fano payloads.
- Trie reader/iterator invariants: exact seek, inexact seek, `Next`, `Prev`, empty trie, prefix keys, chain compression, dense/sparse traversal, sparse binary-search fallback, full scans, move behavior, and progressive truncation rejection.
- UDI API invariants: builder/reader status behavior, comparator validation, null comparator defaults, bounds preparation, multi-scan state advancement, wrapper internal-key materialization, empty-index seek results, and corrupted index data handling.
- Same-user-key invariants: same-key boundary detection, overflow run seek/next/prev, zero sequence numbers, packed value-type tags, BFS-reordered overflow metadata, last-block tag handling, non-boundary sentinel behavior, and randomized block layouts.
- SST integration signals: reading with and without trie UDI, upper-bound iteration, small SSTs, mixed key types, large multi-block SSTs, deleted-key seek advancement, and compression dictionary replay.

Running this file's test binary exercises both unit-level serialized structure validation and end-to-end RocksDB table integration for the trie UDI implementation.
