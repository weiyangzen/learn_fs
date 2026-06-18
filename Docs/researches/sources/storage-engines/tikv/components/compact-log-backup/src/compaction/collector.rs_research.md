# sources/storage-engines/tikv/components/compact-log-backup/src/compaction/collector.rs

## Purpose
Transforms streams of backup log metadata into executable `Subcompaction` groups. It supports ordinary grouping by logical files and cache-aware grouping by physical-file cache windows.

## APIs and control flow
`CollectSubcompaction<S>` wraps a `Stream<Item = Result<LogFile>>`. It filters metadata/out-of-range files, groups files by `SubcompactionCollectKey`, emits a group when accumulated size exceeds `subcompaction_size_threshold`, and flushes pending undersized groups at stream end. `CollectCachedSubcompaction<S>` consumes `PhysicalLogFile` streams, registers physical files in `PhysicalFileCache`, defers a file when capacity is full, forces pending groups into a ready queue, waits for capacity, and resumes. Ready groups are sorted by input count, size, region, CF, file type, meta flag, and table id; matching pending groups can be merged before yielding when under threshold.

`CollectSubcompactionConfig` carries `compact_shift_from_ts`, `compact_from_ts`, `compact_to_ts`, and size threshold. `take_statistic` drains collection counters.

## State, dependencies, and integration
Collector state is `HashMap<SubcompactionCollectKey, UnformedSubcompaction>`, delayed final groups, cache wait futures, deferred physical files, ready queues, and statistics. It depends on Tokio streams, `engine_traits::{CF_DEFAULT,CfName}`, `PhysicalFileCache`, log storage types, and error tracing. The output feeds `SubcompactionExec`.

## Risks and test signals
Timestamp filtering uses `compact_shift_from_ts` only for default CF, which is subtle. Meta files are excluded. Cache mode must not deadlock when capacity is full; it relies on ref guards in execution to release capacity. Tests cover normal grouping, cache full waits and forced drains, pending merge thresholds, error propagation, timestamp filtering, group keys, default-CF shift bounds, and region epoch hint aggregation.
