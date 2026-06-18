# sources/storage-engines/rocksdb/db/seqno_time_test.cc

## Purpose

`seqno_time_test.cc` is the regression suite for RocksDB sequence-number-to-time tracking, table-property encoding of that mapping, last-level hot/cold data placement, pre-populated mappings, and packed value helpers. It uses a mock clock to make time-sensitive behavior deterministic.

## Important APIs, Types, and Helpers

`SeqnoTimeTest` derives from `DBTestBase`, installs `MockSystemClock` through `CompositeEnvWrapper`, and overrides the periodic task scheduler timer with `SyncPoint`. `AssertKeyTemperature` checks IO stats and file temperature. `SeqnoTimeTablePropTest` parameterizes three option modes: `preserve_internal_time_seconds`, `preclude_last_level_data_seconds`, and both set with tracking duration determined by the smaller preserve value.

The tests exercise `SeqnoToTimeMapping` methods including `Append`, `SetCapacity`, `SetMaxTimeSpan`, `GetProximalSeqnoBeforeTime`, `GetProximalTimeBeforeSeqno`, `PrePopulate`, `CopyFromSeqnoRange`, `Enforce`, `AddUnenforced`, `EncodeTo`, and `DecodeFrom`. They also cover `PackValueAndWriteTime`, `ParsePackedValueWithWriteTime`, `PackValueAndSeqno`, and `ParsePackedValueWithSeqno`.

## Control Flow and State Behavior

`TemperatureBasicUniversal` and `TemperatureBasicLevel` write keys over simulated time, compact them, and verify hot data remains in proximal levels while old data moves to cold last-level files. They assert both file-temperature sizes and actual read IO temperature stats.

`BasicSeqnoToTimeMapping` writes at varying intervals, flushes SSTs, decodes each table's `seqno_to_time_mapping`, and validates sample counts and proximal sequence estimates. `MultiCFs` checks scheduler activation only when at least one CF needs tracking, in-memory mapping capacity behavior across CF options, compaction output mappings, and cleanup after dropping CFs. `MultiInstancesBasic` verifies multiple DB instances can run the periodic worker.

`SeqnoToTimeMappingUniversal` verifies universal compaction preserves mappings, avoids sequence zeroing while data is still hot, then zeroes expired sequences and eventually pushes all data to the last level. `PrePopulateInDB` documents when mappings are pre-populated for new DBs, not read-only opens, and how preallocated sequence numbers remain monotonic across reopen.

The remaining tests validate the pure mapping data structure: append merge rules, capacity/time-span enforcement, proximal query semantics, prepopulation interpolation, copying a sequence range, sorting/cleanup of unenforced mappings, compact encode/decode reduction, and minimizing time gaps during reduction.

## Persistence, Dependencies, and Integration

Persistent state under test includes table properties containing encoded seqno-time mappings, sequence numbers in SST keys, file temperatures, compaction placement, and DB latest sequence after prepopulation. The suite integrates options, periodic task scheduling, mock time, compaction, table properties, IO stats by temperature, multiple CFs, read-only open, and universal/level compaction.

## Risks and Test Signals

Risk areas include approximate mapping accuracy, capacity reductions biasing too new or too old, periodic worker lifecycle, CF option aggregation, preallocated sequence numbers, and interactions between last-level temperature and compaction sequence zeroing. Strong signals are decoded table mappings with expected sizes, proximal sequence bounds, temperature-specific SST sizes and read stats, scheduler task presence/absence, monotonic latest sequence after prepopulation, and correct packed-value round trips.
