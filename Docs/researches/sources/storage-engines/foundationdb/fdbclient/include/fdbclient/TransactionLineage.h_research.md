<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TransactionLineage.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TransactionLineage.h

## Purpose
`TransactionLineage.h` declares actor-lineage metadata for transaction operations so sampled actor stacks can report transaction IDs and the current high-level operation.

## Important APIs, Types, and Functions
Important exports are `TransactionLineage`, its `Operation` enum, `TransactionLineageCollector`, and, when `ENABLE_SAMPLING` is defined, `ScopedLineage<T,V>` plus `make_scoped_lineage`. Operations include get value, get key, get range, watch, get read version, commit, and key-server location lookup.

## Control Flow
Transaction code writes lineage fields into the current actor lineage. The collector reads optional `txID` and `operation` values and converts them into a map of human-readable properties. `ScopedLineage` temporarily replaces one lineage member and restores the previous value when leaving scope unless moved or released.

## State and Persistence Behavior
Lineage state is in-memory diagnostic metadata associated with actor execution. It is not persisted to the database. The scoped helper mutates the current lineage and relies on RAII to restore values across normal control flow.

## Dependencies and Integration Points
The header depends on `ActorLineageProfiler.h` and integrates with NativeAPI transaction actors, sampling builds, profiling collectors, and diagnostics that inspect actor lineage trees.

## Risks and Edge Cases
The scoped helper only exists under `ENABLE_SAMPLING`, so instrumentation code must be compiled conditionally. Move assignment restores the old value before taking ownership, which is correct but easy to misuse if stored in containers. Collector output intentionally omits unset fields, so missing lineage may mean either no operation or disabled sampling.

## Test Signals
Sampling/profiler tests, actor-lineage collector tests, and transaction operation instrumentation tests are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TransactionLineage.h -->
