# sources/storage-engines/pebble/wal/wal.go

## Purpose
Defines shared WAL package contracts: directory metadata, logical WAL numbering, physical filename parsing, manager/writer/reader interfaces, failover options, event payloads, stats, deletion records, and offsets.

## Important APIs, Types, And Functions
Important exported items are `StableIdentifierFilename`, `Dir`, `NumWAL`, `LogNameIndex`, `ParseLogFilename`, `Options`, `Init`, `Options.Dirs`, `FailoverOptions`, `FailoverOptions.EnsureDefaults`, `EventListener`, `CreateInfo`, `Stats`, `FailoverStats`, `Manager`, `DeletableLog`, `SyncOptions`, `Writer`, `RefCount`, `Reader`, and `Offset`.

## Control Flow
`Init` selects `StandaloneManager` when `Options.Secondary` is empty and `failoverManager` otherwise, then delegates initialization with the existing scanned `Logs`. `ParseLogFilename` accepts backward-compatible `NNNN.log` names as log index zero and failover segment names of the form `NNNN-III.log`; non-WAL `.log` files that do not parse as disk file numbers are ignored. `FailoverOptions.EnsureDefaults` fills probe, health, sampling, threshold, and elevated-stall defaults.

## State And Persistence Behavior
`Dir.ID` is a stable persisted directory identity used to detect incorrect secondary WAL mounts. The `Manager` abstraction owns durable WAL lifecycle, while `Writer` exposes append, close, and record-layer metrics. `Offset` records physical replay location and prior segment byte count for failover-aware diagnostics.

## Dependencies And Integration Points
Integrates with Pebble options, DB recovery, commit pipeline synchronization, event listeners, Prometheus histograms, file locks, `record.LogWriter`, and virtual WAL readers. The package documents that the manifest knows only logical WAL numbers; this package reconstructs physical segment mappings from directory contents.

## Risks And Edge Cases
Filename parsing intentionally ignores unrelated `.log` files to preserve CockroachDB compatibility. Failover defaults govern write-stall and failback behavior, so too-aggressive thresholds can cause unnecessary directory switches, while too-lax thresholds hurt latency. `WriteRecord` may retain the caller buffer unless a `RefCount` is supplied. `Manager.Obsolete` must not delete unflushed WALs.

## Test Signals
Signals appear in WAL filename/list tests, failover manager tests elsewhere, standalone manager behavior, and `wal_failover_identifier_test.go` for stable secondary identifiers.
