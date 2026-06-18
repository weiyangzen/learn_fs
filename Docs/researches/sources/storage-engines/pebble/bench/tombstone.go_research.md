# sources/storage-engines/pebble/bench/tombstone.go

## Purpose
`tombstone.go` composes a YCSB workload with the queue workload to measure behavior under sustained point-tombstone generation and mixed read/write pressure.

## Important APIs, Types, And Functions
`TombstoneConfig`, `DefaultTombstoneConfig`, and `RunTombstone` are the main APIs. The config nests `YCSBConfig` and `QueueConfig`.

## Control Flow
`RunTombstone` validates incompatible wipe/prepopulated-key settings, parses YCSB workload and key distribution, creates a `ycsb` runner and queue `Test`, then uses `RunTest` with combined init/run callbacks. Ticks gather queue operation deltas, YCSB histogram deltas, estimate disk usage for the queue key range, and print both queue and YCSB throughput.

## State And Persistence Behavior
The benchmark persists both YCSB data and queue keys in one Pebble DB. Queue operations continuously add tombstones and new keys; YCSB adds read/write/scan pressure. `EstimateDiskUsage` observes the queue key range's storage footprint.

## Dependencies And Integration Points
It depends on `ycsb.go`, `queue.go`, `pebbleDB` internals, `humanize`, and `RunTest`. It type-asserts the benchmark DB to `pebbleDB` to access `EstimateDiskUsage`.

## Risks And Edge Cases
The type assertion means alternate `DB` implementations cannot run this benchmark unchanged. The queue and YCSB workers run indefinitely until the harness stops. `EstimateDiskUsage` errors are fatal. Wipe/prepopulation validation prevents a nonsensical destructive configuration.

## Test Signals
No direct tests. Runtime output shows queue size and throughput trends.
