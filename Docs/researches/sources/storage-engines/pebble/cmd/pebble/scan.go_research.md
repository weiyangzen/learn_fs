<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/scan.go -->
# sources/storage-engines/pebble/cmd/pebble/scan.go

## Purpose
Defines `pebble bench scan <dir>`, a scan benchmark wrapper.

## Important APIs, Types, and Functions
`scanConfig` is `bench.DefaultScanConfig()`. `scanCmd` binds usage and exact-arg validation. `init` adds `--reverse`, `--rows`, and `--values`. `runScan` assigns a rate limiter and calls `bench.RunScan`.

## Control Flow
The command parses flags, constructs `commonCfg.RateLimiter` from `maxOpsPerSec`, and delegates execution to the benchmark package.

## State and Persistence Behavior
Only config globals are changed here. The benchmark may open or populate a DB under the supplied directory depending on `commonCfg`.

## Dependencies and Integration Points
Depends on Cobra and `bench.ScanConfig`. It uses common flags bound in `main.go` such as cache, duration, concurrency, WAL, wipe, shared storage, and rate.

## Risks and Edge Cases
`Run` rather than `RunE` means benchmark errors, if any, must be handled internally by `bench.RunScan`. Global config reuse can affect repeated runs.

## Test Signals
No direct tests. Signals are correct scan direction, row/value distribution parsing, and rate limiter propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/scan.go -->
