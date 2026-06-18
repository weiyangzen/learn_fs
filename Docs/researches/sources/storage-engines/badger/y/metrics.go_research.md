# sources/storage-engines/badger/y/metrics.go

## Purpose
This file declares global expvar metrics and guarded helper functions for Badger read/write, LSM, value-log, compaction, and size counters.

## Important APIs, Types, And Functions
`BADGER_METRIC_PREFIX` is `badger_`. Global metrics include `lsmSize`, `vlogSize`, `pendingWrites`, VLOG read/write counts and bytes, LSM bytes and bloom/get maps, and user operation counters. Public helper functions add to counters or set/get map values only when an `enabled` flag is true. Internal helpers are `addInt`, `addToMap`, `storeToMap`, and `getFromMap`.

## Control Flow
Package `init` registers all metrics through `expvar.NewInt` or `expvar.NewMap`. Callers pass `Options.MetricsEnabled`; disabled calls return without touching global expvar state.

## State And Persistence Behavior
Metrics are process-global and cumulative across DB instances. They are not persisted, but tests can observe them through `expvar.Get`.

## Dependencies And Integration Points
Value-log writes/reads, DB get/put paths, compactions, and size reporters call these helpers. `value_test.go` uses `badger_get_num_user` to validate rewrite lookup avoidance.

## Risks And Edge Cases
Global expvar names can conflict if the package is initialized multiple times in unusual plugin/test environments. Metrics are shared across DBs, so tests must clear or isolate counters when asserting exact values.

## Test Signals
There is no dedicated metrics test here. Integration tests detect selected counter behavior.
