# sources/object-store/daos/src/engine/srv_metrics.c

## Purpose
`srv_metrics.c` initializes global engine telemetry metrics that report startup readiness, rank identity, and received dead-rank event activity.

## Important APIs, Types, and Functions
It defines the global `struct engine_metrics dss_engine_metrics` and exports `dss_engine_metrics_init(void)` and `dss_engine_metrics_fini(void)`. Metrics created include `started_at`, `servicing_at`, `rank`, `events/dead_ranks`, and `events/last_event_ts`.

## Control Flow
`dss_engine_metrics_init` zeroes the global metrics struct, then creates each telemetry node with `d_tm_add_metric`. It returns immediately on any creation failure, logging the specific metric that failed. `dss_engine_metrics_fini` currently has no cleanup work and returns success.

## State and Persistence Behavior
The file owns process-global telemetry node pointers. Values are recorded elsewhere: `init.c` records startup and ready timestamps, sets rank, and CART event callbacks increment dead-rank counters and update last-event timestamp. Metrics are live telemetry state, not durable storage.

## Dependencies and Integration Points
It depends on `srv_internal.h` for `struct engine_metrics` and on GURT telemetry producer APIs. Initialization is called after `d_tm_init` in `server_init`; metrics are consumed by `init.c` and event callbacks.

## Risks
Partial initialization leaves some metric pointers NULL if a later metric creation fails. Callers that record metrics should tolerate missing telemetry nodes according to telemetry API semantics. `fini` doing nothing is correct only if telemetry teardown is centralized in `d_tm_fini`.

## Test Signals
Tests should inject `d_tm_add_metric` failures at each metric, verify successful node names and types, confirm startup/ready/rank/dead-rank updates from `init.c`, and run shutdown under telemetry leak detection.
