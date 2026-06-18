<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/FastTriggeredWatches.toml -->
# sources/storage-engines/foundationdb/tests/slow/FastTriggeredWatches.toml

## Purpose
Exercises FastTriggeredWatches with a long connection-failure disable window.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): FastTriggeredWatchesTest. Workload entry points are `FastTriggeredWatches`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `FastTriggeredWatches`.

## State And Persistence Behavior
Persistent and simulated state touched: primarily transient workload state and simulation status.
Clear/setup flags and state controls are declared on tests as: FastTriggeredWatchesTest: connectionFailuresDisableDuration=100000, timeout=1500.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
risk is mainly coverage drift if the named workload implementation changes while this config remains unchanged.

## Test Signals
The presence of the configured workload as a slow simulation test is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/FastTriggeredWatches.toml -->
