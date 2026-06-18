<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ExcludeIncludeStorageServers.toml -->
# sources/storage-engines/foundationdb/tests/slow/ExcludeIncludeStorageServers.toml

## Purpose
Runs ExcludeIncludeStorageServers with a data-distribution knob disabling max shards on large teams.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): ExcludeIncludeStorageServers. Workload entry points are `ExcludeIncludeStorageServers`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `ExcludeIncludeStorageServers`.

## State And Persistence Behavior
Persistent and simulated state touched: primarily transient workload state and simulation status.
Clear/setup flags and state controls are declared on tests as: ExcludeIncludeStorageServers: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: dd_max_shards_on_large_teams=0.

## Risks
risk is mainly coverage drift if the named workload implementation changes while this config remains unchanged.

## Test Signals
The presence of the configured workload as a slow simulation test is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ExcludeIncludeStorageServers.toml -->
