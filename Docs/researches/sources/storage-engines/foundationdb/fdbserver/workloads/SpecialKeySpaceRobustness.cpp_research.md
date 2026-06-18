# sources/storage-engines/foundationdb/fdbserver/workloads/SpecialKeySpaceRobustness.cpp

## Purpose
`SpecialKeySpaceRobustnessWorkload` exercises management special-key APIs in scenarios that can run under failure injection. It focuses on idempotency, error schema validity, locking behavior, consistency-check toggles, coordinator reads, advance-version behavior, and conflict ranges for DD mode changes.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `SpecialKeySpaceRobustness`. Important helpers are `getRangeResultInOrder`, `runExcludeAndGetVersionKey`, and `managementApiCorrectnessActor`. It uses `SpecialKeySpace::getManagementApiCommandPrefix`, `getManagementApiOptionsSet`, `getWorkers`, `JSONSchemas::managementApiErrorSchema`, database lock keys, consistency-check keys, coordinator keys, `advanceversion`, DD mode keys, and move-keys lock keys.

## Control Flow
Only client 0 runs. The actor first writes all management options and checks ordered range output. It verifies invalid `exclude` writes produce schema-valid errors, tests repeated exclude/failed commands only update version keys once, validates `setclass` reads/RYW behavior and invalid class errors, checks class source updates, locks the database and verifies normal reads fail with `database_locked`, unlocks, toggles consistencycheck off and back on, reads coordinators through special keys, forces advance version until read versions exceed the target, and proves DD mode writes conflict with transactions reading move-key lock keys.

## State And Persistence Behavior
The workload writes management command special keys that translate into system metadata changes: exclusions, failed lists, process class source, database lock state, consistency-check suspend state, coordinator-derived reads, advance-version recovery, and DD mode updates. It carefully clears lock and consistencycheck state before completion.

## Dependencies And Integration Points
It depends on ManagementAPI, ReadYourWrites, Schemas, SpecialKeySpace, system metadata keys, worker discovery, cluster connection strings, and lock-aware/raw/special-write transaction options. Unlike the correctness workload, it is intended to tolerate some retriable errors from failure injection.

## Risks And Edge Cases
The workload performs real management actions, so cleanup is critical. It handles `commit_unknown_result`, already locked database, empty worker lists, process reboot changing class source back to command-line, and transient GRV/throttling errors. Advance-version expects commit failure while recovery advances the cluster version.

## Test Signals
Assertions and `TestFailure` traces flag ordering or semantic violations. Debug traces identify unexpected special-key API errors, lock/unlock failures, setclass/exclude cases, advance-version progress, and DD conflict behavior. `check` returns true, so actor assertions/errors are the practical failure signal.
