<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageWiggleMetrics.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageWiggleMetrics.h

## Purpose
`StorageWiggleMetrics.h` models persistent metrics and control data for perpetual storage wiggle, the process that periodically moves storage servers to refresh placement. It also provides transaction helpers for delay accounting and metric updates in system keyspace.

## Important APIs, Types, and Functions
Important types include `StorageWiggleMetrics`, `StorageWiggleDelay`, `StorageWiggleData`, and nested `StorageWiggleData::DataForDc`. Helpers include `toJSON`, `reset`, `addPerpetualWiggleDelay_impl`, `resetStorageWiggleMetrics_impl`, `addPerpetualWiggleDelay`, `clearPerpetualWiggleDelay`, `resetStorageWiggleMetrics`, and `updateStorageWiggleMetrics`.

## Control Flow
Wiggle code updates start/finish timestamps and smoothed duration totals, serializes only the persisted scalar fields and smoother totals, and reconstructs smoothers when deserializing. Delay updates run inside transactions with system-key and lock-aware options, fetch the current delay object, add a delta, and write it back. Metric updates first read the perpetual wiggle speed key and only store metrics if wiggle remains enabled.

## State and Persistence Behavior
Metrics and delay state are persisted under `perpetualStorageWigglePrefix`, `perpetualStorageWiggleStatsPrefix`, and DC-specific primary or remote subspaces. `StorageWiggleMetrics::reset` clears counters and timestamps while carrying forward smoother accumulated totals. All database helpers explicitly access system keys and lock-aware transactions.

## Dependencies and Integration Points
The file depends on `Smoother`, Flow serialization, `SystemData`, `KeyBackedTypes`, and `RunTransaction`. It integrates with data distribution, status JSON generation, fdbcli/status consumers, and primary/remote region storage wiggle orchestration.

## Risks and Edge Cases
The anonymous helper namespace in a header creates per-translation-unit helper definitions, which is acceptable for templates but can surprise readers. Clock-derived epoch timestamps rely on caller-provided values. `updateStorageWiggleMetrics` silently probes rather than writing if wiggle is disabled, so callers must not assume a successful future implies persistence. System-key access options are mandatory and easy to omit in new helper paths.

## Test Signals
Signals include perpetual wiggle simulation tests, status JSON checks, system-key persistence round trips, primary and remote region coverage, and tests that disable wiggle while updates race with metric writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageWiggleMetrics.h -->
