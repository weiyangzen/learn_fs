# sources/storage-engines/rocksdb/db/merge_helper.h

## Purpose
`merge_helper.h` declares `MergeHelper`, the compaction/read helper that resolves RocksDB merge operands, and `MergeOutputIterator`, a lightweight view over the last merge result. It defines the public merge helper contract, overload tags for base-value shapes, and the state exposed to compaction code.

## Important APIs, types, and functions
The `MergeHelper` constructor accepts `Env`, user comparator, merge operator, optional compaction filter, logger, internal-key assertion mode, latest snapshot, optional `SnapshotChecker`, compaction level, statistics, and shutdown flag.

`NoBaseValueTag`, `PlainBaseValueTag`, and `WideBaseValueTag` disambiguate `TimedFullMerge` overloads. The overloads construct `MergeOperationInputV3::ExistingValue` from no base, a plain slice, serialized wide-column entity, or `WideColumns`, then delegate to `TimedFullMergeImpl`.

`MergeUntil` consumes an `InternalIterator` positioned at a merge record and returns OK, `MergeInProgress`, `Corruption`, or `ShutdownInProgress`. It takes range deletion aggregation, a sequence boundary, bottommost/history certainty, error logging policy, blob fetcher, full-history timestamp lower bound, blob prefetch buffers, and compaction iteration stats.

`FilterMerge`, `keys`, `values`, `TotalFilterTime`, `HasOperator`, and `FilteredUntil` expose compaction-filter and output state. Private `TimedFullMergeCommonImpl` and `TimedFullMergeImpl` overloads perform merge invocation and output conversion. `IsShuttingDown` is a best-effort relaxed atomic check.

`MergeOutputIterator` binds to a `MergeHelper`, seeks to the first output, advances, and exposes key/value slices from reverse iterators over the helper's result containers.

## Control flow
The header documents that `MergeUntil` proceeds through operands until corruption, put/delete, different user key, snapshot boundary, compaction-filter skip, or iterator end. Results are stored in `keys()` and `values()` until the next `MergeUntil`. Successful full merge usually returns one key/value pair with the newest sequence and a value-like type. If a complete merge is impossible, the helper returns merge operands in traversal order for compaction to write forward.

`TimedFullMerge` is used by both compaction and point reads. Compaction uses the overload that exposes a serialized result and value type; point reads use the overload that translates V3 output into a plain value or `PinnableWideColumns`.

## State and persistence behavior
The helper holds transient output state only. `keys_` stores internal keys, and `merge_context_` stores corresponding operands. Filter state includes total nanoseconds, changed value buffer, and skip-until internal key. Although transient, this state determines compaction output records and therefore has persistence consequences when written into SST files.

## Dependencies and integration points
The declaration connects merge code with `MergeContext`, range deletion aggregation, snapshot checking, wide-column serialization, compaction filters, environment/clock timing, RocksDB merge operator APIs, slices, wide columns, stop watches, blob fetching, prefetch buffers, and compaction iteration stats. It is consumed by compaction iterators and memtable point-read helpers.

## Risks and edge cases
`MergeUntil` requires the input iterator's first key to be an uncorrupted merge key. `keys()` and `values()` lifetimes end at the next merge call. The helper's behavior changes based on `at_bottom`, `latest_snapshot_`, `SnapshotChecker`, timestamp lower bounds, and merge operator support for partial/single operand merges. Callers must supply blob fetch infrastructure when blob indexes can be encountered.

## Test signals
`merge_helper_test.cc` is the focused contract test for `MergeUntil` and `MergeOutputIterator`; `merge_test.cc` exercises `TimedFullMerge` and full DB integration. Wide-column and blob merge paths should be covered by broader wide-column/blob compaction tests.
