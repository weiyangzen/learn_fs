<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/MoveKeysClean.toml -->
# sources/storage-engines/foundationdb/tests/slow/MoveKeysClean.toml

## Purpose
Moves keys while Sideband, light clogging, rollback, and coordinator changes run.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): MoveKeysNew. Workload entry points are `Sideband`, `RandomClogging`, `Rollback`, `RandomMoveKeys`, `ChangeConfig`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Sideband`(testDuration=300.0); `RandomClogging`(testDuration=300.0, scale=0.5, clogginess=0.1); `Rollback`(testDuration=300.0, meanDelay=150.0); `RandomMoveKeys`(testDuration=300.0, meanDelay=2); `ChangeConfig`(maxDelayBeforeChange=300.0, coordinators='auto').

## State And Persistence Behavior
Persistent and simulated state touched: cluster topology, failure, rollback, data movement, or configuration state.
Clear/setup flags and state controls are declared on tests as: MoveKeysNew: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
failure workloads may expose timing-sensitive recovery behavior and can stretch configured timeouts.

## Test Signals
failure workloads provide recovery and resilience signals
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/MoveKeysClean.toml -->
