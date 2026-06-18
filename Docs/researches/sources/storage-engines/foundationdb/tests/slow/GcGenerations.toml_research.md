<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/GcGenerations.toml -->
# sources/storage-engines/foundationdb/tests/slow/GcGenerations.toml

## Purpose
Runs Cycle plus GcGenerations in a multi-region remote-double configuration with recovery tracking knobs.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): GcGenerations. Workload entry points are `Cycle`, `GcGenerations`. Configuration keys include configuration=generateFearless=True, processesPerMachine=1, machineCount=20, minimumRegions=2, coordinators=1, remoteConfig='remote_double'.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(nodeCount=3000, transactionsPerSecond=250.0, testDuration=300.0); `GcGenerations`(testDuration=1000.0).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation.
Clear/setup flags and state controls are declared on tests as: GcGenerations: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: max_write_transaction_life_versions=5000000, record_recover_at_in_cstate=True, track_tlog_recovery=True, cc_recovery_init_req_growth_factor=1.01.

## Risks
risk is mainly coverage drift if the named workload implementation changes while this config remains unchanged.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/GcGenerations.toml -->
