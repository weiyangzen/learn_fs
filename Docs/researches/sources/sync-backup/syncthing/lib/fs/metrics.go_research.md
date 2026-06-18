# sources/sync-backup/syncthing/lib/fs/metrics.go

## Purpose
Wraps filesystem and file operations with Prometheus counters for operation count, duration, and bytes transferred.

## Important APIs, Types, and Functions
Metric vectors `metricTotalOperationSeconds`, `metricTotalOperationsCount`, `metricTotalBytesCount`; constants for operation labels; `metricsFS`; `metricsFile`; `account`; method wrappers for all `Filesystem` and `File` operations.

## Control Flow
Each wrapper defers an accounting closure that records duration, increments count, and records bytes when available. File-returning methods wrap successful files in `metricsFile`, whose `Read`, `ReadAt`, `Write`, and `WriteAt` record byte counts.

## State and Persistence Behavior
Metrics are process-global Prometheus counters labeled by filesystem root URI and operation. No filesystem state is altered beyond delegated operations.

## Dependencies and Integration Points
Always applied by `NewFilesystem`. Integrates with `promauto` and wrapper unwrapping through `underlying` and `metricsFile.unwrap`.

## Risks
`account` calls `m.next.URI()` for every operation, which can itself be nontrivial or instrumented below if wrapper ordering changes. The label typo `mdkir` for mkdir is stable but misspelled. Metrics cardinality follows filesystem URI values.

## Test Signals
No direct metric assertions in this subset; package tests exercise wrappers indirectly through `NewFilesystem`.
