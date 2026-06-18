# sources/object-store/daos/src/container/srv_metrics.c

## Purpose
Allocates and frees container-server telemetry counters for successful container operations. It is intentionally small and scoped to pool-level container metrics.

## Important APIs
- `ds_cont_metrics_alloc(const char *path, int tgt_id)` allocates `struct cont_pool_metrics` and adds counters under the supplied telemetry path.
- `ds_cont_metrics_count()` reports the number of telemetry node pointers in `struct cont_pool_metrics`.
- `ds_cont_metrics_free(void *data)` frees the allocated metrics structure.

## Control flow
Allocation asserts `tgt_id < 0`, making these global/pool metrics rather than per-target metrics. It allocates the metrics struct, then attempts to register counters for open, close, query, create, and destroy operations using `d_tm_add_metric()`. Individual metric registration failures are logged as warnings but do not abort allocation; callers receive the metrics struct even if some node pointers remain unset.

## State and persistence behavior
The file manages volatile telemetry node pointers only. It has no persistent state and does not increment counters itself; other container service paths are expected to use the returned `cont_pool_metrics` fields.

## Dependencies and integration
Depends on `srv_internal.h` for `struct cont_pool_metrics` and on `gurt/telemetry_producer.h` for producer APIs. It is integrated through the server module metrics allocation hooks declared in `srv_internal.h`.

## Risks
Because partial metric registration succeeds, consumers must tolerate NULL metric nodes. `ds_cont_metrics_count()` assumes the structure contains only `struct d_tm_node_t *` fields; adding a non-pointer field without changing this helper would break count semantics. The function only frees the struct, relying on telemetry infrastructure ownership for metric nodes.

## Test signals
Tests should cover successful metric creation paths, simulated `d_tm_add_metric()` failures, the count helper after structure changes, and callers that increment counters when some nodes are NULL.
