# sources/storage-engines/rocksdb/db/prefix_test.cc

## Purpose
`prefix_test.cc` tests prefix-aware memtable and iterator behavior using a custom binary key comparator. It covers prefix hash memtable factories, prefix bloom/filter behavior, prefix-limited iteration, mixed Put/Merge/Delete histories, backward iteration in prefix seek mode, and several performance/profiling flows gated by gflags.

## Important APIs, Types, And Functions
When `GFLAGS` is unavailable, the file builds a stub `main` that prints a skip message. With gflags, it defines flags controlling bucket counts, prefix/random workloads, write buffers, memtable prefix bloom, huge pages, value size, and debug printing.

`TestKey` stores `prefix` and `sorted` `uint64_t` fields. `TestKeyToSlice` and `SliceToTestKey` encode/decode fixed64 binary keys. `TestKeyComparator` compares by prefix first, then suffix, and supports prefix-only slices. Helpers `PutKey`, `MergeKey`, `DeleteKey`, `SeekIterator`, and `Get` operate on encoded keys.

`SamePrefixTransform` is a `SliceTransform` that maps all keys in a configured domain to one fixed prefix. `PrefixTest` configures DB options with `TestKeyComparator`, fixed 8-byte prefix extractor, block-based Bloom filter with whole-key filtering disabled, and selectable hash skip-list/hash link-list memtable factories.

## Control Flow
`SamePrefixTest.InDomainTest` verifies a transform whose domain excludes some keys does not break seeking/flushing for keys outside the domain.

`TestResult` iterates over hash memtable options and one/two buckets, inserting keys into the same and different prefixes. It verifies `Seek`, `Next`, and `Get` return expected values for head, middle, tail, smaller-prefix, and larger-prefix cases.

`PrefixValid` writes keys for one prefix plus a deleted key in another prefix, enables `prefix_same_as_start`, and verifies iteration stops at the prefix boundary and seeking past the prefix returns invalid. `DynamicPrefixIterator` bulk-loads many prefixes, optionally shuffled, then profiles puts, existing-prefix scans, and non-existing seeks. A flag can intentionally delete during scans to reproduce deadlock scenarios.

`PrefixSeekModePrev` builds three layers of entries using puts/merges/deletes, tracks expected visible state in `std::map`, and randomly alternates `Next` and `Prev` within a prefix to compare iterator values with the map. `PrefixSeekModePrev2` targets a case where a child iterator becomes invalid due to Bloom filtering during reverse movement. `PrefixSeekModePrev3` verifies `SeekToLast` respects `iterate_upper_bound` in prefix seek mode.

## State And Persistence Behavior
The tests create real DB state with memtables and flushed SSTs. Prefix behavior is exercised across both mutable/immutable memtables and table files. Merge and delete histories are included so iterator traversal must resolve internal records correctly, not just scan sorted puts.

The comparator supports prefix-only keys, allowing prefix extractor outputs to participate in comparisons. `prefix_same_as_start` changes iterator validity: iteration is expected to stop when leaving the starting prefix.

## Dependencies And Integration Points
The file depends on DBImpl test hooks, block-based table Bloom filters, memtable factories (`HashSkipList`, `HashLinkList`, `SkipList`), perf context, histograms, stop watches, gflags compatibility, fixed64 coding, merge operators, and a custom comparator/prefix extractor pair.

Integration points include memtable prefix hashing, memtable prefix Bloom, block-based prefix Bloom with whole-key filtering disabled, iterator prefix mode, `SeekForPrev`/`Prev` across merging iterators, `iterate_upper_bound`, merge resolution, and DB flush/reopen lifecycle.

## Risks
Prefix iteration is intentionally narrower than total-order iteration. If callers set `prefix_same_as_start`, seeking outside or past a prefix can produce invalid results even when later keys exist. The tests document that boundary.

The custom comparator decodes fixed64 from slices and assumes valid key sizes except for prefix-only cases. Arbitrary strings would be unsafe with this comparator. The dynamic performance test can be expensive with default high prefix counts, and `trigger_deadlock` intentionally performs deletes during iteration.

Reverse prefix movement is particularly fragile because child iterators can be invalidated by Bloom filters or upper bounds. The last three tests target those edge cases.

## Test Signals
Success signals include exact values from `Get` and iterator movement within prefix groups, invalid iterators when seeking outside prefix constraints, matching iterator/map values while alternating `Next` and `Prev`, no deadlock unless intentionally requested, correct `Prev` result after a seek gap, and `SeekToLast` returning the last key below the upper bound.
