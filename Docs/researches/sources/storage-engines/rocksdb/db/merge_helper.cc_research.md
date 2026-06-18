# sources/storage-engines/rocksdb/db/merge_helper.cc

## Purpose
`merge_helper.cc` implements merge resolution used mainly by compaction and by point lookup helper wrappers. It turns stacks of merge operands plus optional base values into final values, partial-merge operands, or merge-in-progress outputs while respecting snapshots, range tombstones, blob values, wide columns, compaction filters, user-defined timestamps, and shutdown.

## Important APIs, types, and functions
The constructor stores environment, clock, user comparator, merge operator, optional compaction filter, logger, snapshot state, snapshot checker, compaction level, statistics, shutdown flag, and `allow_single_operand_` from the merge operator.

`TimedFullMergeCommonImpl` invokes `MergeOperator::FullMergeV3`, records read merge operand histograms and merge operation time, maps failures to `Status::Corruption`, and returns the operator failure scope when requested.

Two `TimedFullMergeImpl` overloads translate V3 merge output. The iterator/compaction overload returns serialized data plus `ValueType`, supporting plain values, wide-column entities, and returned operand slices. The point-lookup overload fills either `std::string` or `PinnableWideColumns`, including default-column extraction when the caller requested a plain value.

`MergeUntil` is the main loop. `MergeOutputIterator` iterates the helper's last output. `FilterMerge` applies `CompactionFilter::FilterV4` to merge operands and validates `RemoveAndSkipUntil` targets.

## Control flow
`MergeUntil` starts at a merge record and copies the original internal key because iterator keys are invalidated by movement. It parses each internal key, skips range-delete sentinel keys, checks shutdown, stops at corruption when assertions are disabled, stops at a different user key, stops at timestamp GC boundaries, and stops before entries protected by `stop_before`/snapshot checker.

For non-merge base records, it full-merges queued operands with either no base, a plain value, an unpacked timed value, a fetched blob value, or a resolved wide-column entity. Range tombstones can cause an otherwise present base to be treated as no base. Successful full merge rewrites the newest queued key type to `kTypeValue` or `kTypeWideColumnEntity`, clears the operand stack, stores the result, and advances past the base record. Merge operator failures with `kMustMerge` are downgraded to `MergeInProgress` so operands are preserved.

For merge records, the helper optionally applies compaction filters unless the sequence is protected by the latest snapshot. Range tombstones can remove operands. Kept or changed operands are pushed into `MergeContext` with the matching key. `RemoveAndSkipUntil` clears output and records a skip target.

After iteration stops, the helper returns OK if all operands were filtered. If it is certain it has seen the entire key history (`at_bottom` plus next key/end and timestamp GC eligibility), it full-merges with no base and converts output to a value. Otherwise it returns `MergeInProgress` and attempts `PartialMergeMulti` when enough operands are available or the operator allows a single operand.

## State and persistence behavior
State is per-helper and invalidated on each `MergeUntil`: `keys_`, `merge_context_`, compaction filter skip target/value, filter timer totals, and status. No data is persisted directly, but returned keys/values drive compaction output, so mistakes affect SST contents and future recovery. The helper also updates perf counters, statistics ticks, blob read stats, and filter timing.

## Dependencies and integration points
The implementation depends on blob fetch/index/prefetch code, compaction iteration stats, internal key parsing/updating, wide column serialization/resolution, perf context, statistics, comparator timestamp APIs, internal iterators, range deletion aggregators, and compaction filters. It is used by compaction iterator logic and by memtable read helpers through `TimedFullMerge`.

## Risks and edge cases
Operand ordering, timestamp comparisons, and snapshot boundaries are delicate. Full merge over a base must not cross a visible snapshot. Blob indexes require a valid `BlobFetcher`. Wide-column V2 entity blobs must be resolved before V1 merge input. `RemoveAndSkipUntil` is ignored if it does not advance. Merge outputs larger than 4GB are rejected because block builders use 32-bit sizes. `kMustMerge` failure scope must preserve operands instead of dropping data.

## Test signals
`merge_helper_test.cc` covers bottom-level full merge, merge with base value, snapshot stop, non-partial operators, single operands, deletion bases, corrupt keys, compaction filtering, snapshot-protected filtering, and oversized partial merge rejection. `merge_test.cc` covers `TimedFullMerge` oversized full results and DB-level merge behavior.
