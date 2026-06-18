# sources/object-store/daos/src/pool/srv_metrics.c

## Purpose

This file implements telemetry metric allocation and per-pool metric directory lifecycle for the pool server module. It defines the metric nodes registered by `srv.c` through `struct daos_module_metrics pool_metrics`.

## Important APIs, types, and functions

- `ds_pool_metrics_alloc()`: allocates `struct pool_metrics`, records a start timestamp, and creates operation counters and service gauges.
- `ds_pool_metrics_count()`: returns the number of metric node pointers in `struct pool_metrics`.
- `ds_pool_metrics_free()`: frees the metrics container.
- `pool_metrics_gen_path()`: formats `pool/<uuid>`.
- `get_pool_dir_size()`: estimates telemetry directory size.
- `ds_pool_metrics_start()` / `ds_pool_metrics_stop()`: create/finalize per-pool ephemeral telemetry directories and module metrics.

## Control flow

Metric allocation logs but tolerates individual `d_tm_add_metric()` failures, returning the structure unless allocation fails. Starting per-pool metrics creates an ephemeral directory, initializes module metrics on the system tag, and cleans up by calling stop if module metric initialization fails. Stop finalizes module metrics and removes the ephemeral directory.

## State and persistence behavior

Metrics are runtime telemetry state, not persistent pool metadata. Metric pointers live in `struct pool_metrics`; per-pool telemetry path lives in `pool->sp_path`; module metric data lives under `pool->sp_metrics` and telemetry shared memory.

## Dependencies and integration points

It depends on GURT telemetry producer APIs, DAOS server module metric helpers, `struct pool_metrics` from `srv_internal.h`, and `struct ds_pool` fields. Other pool service code increments or sets these nodes for pool operations and service state.

## Risks and test signals

`ds_pool_metrics_count()` assumes every field in `struct pool_metrics` is a `struct d_tm_node_t *`. Metric creation can partially fail, so users must tolerate null nodes. Tests should cover allocation failure, partial metric registration failure, metric count consistency, start cleanup after init failure, stop directory deletion failure, path formatting, and null metric pointer handling.
