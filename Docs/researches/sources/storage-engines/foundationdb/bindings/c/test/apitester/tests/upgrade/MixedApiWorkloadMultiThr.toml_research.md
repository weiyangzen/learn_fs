# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/upgrade/MixedApiWorkloadMultiThr.toml

## Purpose
Long-running mixed workload for upgrade tests with a multi-threaded buggified client.

## Important APIs, types, and functions
Runs `ApiCorrectness`, `CancelTransaction`, `AtomicOpsCorrectness`, and `WatchAndWait` with `runUntilStop = true`, randomized client/database/thread ranges, and DB pooling.

## Control flow
Workloads run until an external controller sends stop/progress commands, supporting cluster upgrades while traffic continues.

## State and persistence behavior
Continuously mutates multiple workload key spaces. Progress is externally observed rather than bounded by fixed operation counts.

## Dependencies and integration points
Requires control-pipe support, upgrade harness orchestration, transaction retries across cluster version changes, and multi-version client compatibility.

## Risks and test signals
No-progress hangs after upgrade and control-pipe failures are key risks. `CHECK_OK`, `DONE`, and continued clean traffic are signals.
