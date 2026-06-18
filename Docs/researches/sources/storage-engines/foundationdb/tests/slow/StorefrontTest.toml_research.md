<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/StorefrontTest.toml -->
# sources/storage-engines/foundationdb/tests/slow/StorefrontTest.toml

## Purpose
Runs a standalone Storefront workload with configured actors, item count, order size, and TPS.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): StorefrontTest. Workload entry points are `Storefront`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Storefront`(actorsPerClient=10, transactionsPerSecond=200, itemCount=10000, maxOrderSize=4).

## State And Persistence Behavior
Persistent and simulated state touched: application key-space data used for correctness validation.
Clear/setup flags and state controls are declared on tests as: StorefrontTest: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
risk is mainly coverage drift if the named workload implementation changes while this config remains unchanged.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/StorefrontTest.toml -->
