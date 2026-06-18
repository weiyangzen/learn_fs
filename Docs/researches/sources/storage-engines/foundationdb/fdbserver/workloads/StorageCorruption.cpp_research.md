# sources/storage-engines/foundationdb/fdbserver/workloads/StorageCorruption.cpp

## Purpose
`StorageCorruptionWorkload` is a negative test for storage corruption detection. It enables a `StorageCorruptionBug`, disables data distribution, lets corruption injection run, then re-enables data distribution and expects consistency checking to report failure.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `StorageCorruption`. Important members are `std::shared_ptr<StorageCorruptionBug> bug`, `SimBugInjector bugInjector`, and `testDuration`. `_start` uses `setDDMode`, bug injector enable/disable, `bug->corruptionProbability`, `bug->numHits`, and `ProcessEvents::uncancellableEvent`.

## Control Flow
The constructor enables the storage corruption bug in the local injector, configures corruption probability, and disables the injector. Client 0 disables DD with `setDDMode(cx, 0)`, enables corruption injection for `testDuration`, sets probability to zero, logs the number of corruption hits, disables injection, registers an uncancellable process event listener for severe `ConsistencyCheckFailure`, and re-enables DD.

## State And Persistence Behavior
The workload intentionally corrupts storage-server state through the bug injector and toggles data distribution mode. It does not write ordinary keys directly. Its success condition is detecting the induced corruption when consistency checking resumes.

## Dependencies And Integration Points
It depends on `StorageCorruptionBug`, `SimBugInjector`, `ManagementAPI::setDDMode`, and `ProcessEvents`. It disables all failure-injection workloads to isolate the corruption signal.

## Risks And Edge Cases
The workload returns true from `check` regardless of whether consistency failure was observed. The positive signal is a trace-event side effect (`NegativeTestSuccess`) registered after corruption injection. If no corruption hits occur during `testDuration`, the negative test may not exercise the target path.

## Test Signals
`CorruptionInjections` reports `bug->numHits()`. A severe `ConsistencyCheckFailure` process event triggers `NegativeTestSuccess`. Actor errors during DD mode changes or bug injection surface as workload failures.
