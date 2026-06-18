# sources/object-store/daos/src/container/srv.c

## Purpose
`srv.c` registers the DAOS container server module. It wires the protocol formats from `rpc.h` to concrete server handlers, initializes/finalizes container module subsystems, creates per-thread container caches, and exposes metrics and module metadata to `daos_server`.

## Important APIs, Types, and Functions
- `init()` initializes container-side infrastructure in dependency order: object ID IV (`ds_oid_iv_init`), container IV (`ds_cont_iv_init`), then default container properties (`ds_cont_prop_default_init`).
- `fini()` tears down the same subsystems, though in the current code it finalizes container IV, OID IV, then default properties.
- `ds_cont_tgt_destroy_co_ops`, `ds_cont_tgt_query_co_ops`, `ds_cont_tgt_epoch_aggregate_co_ops`, and `ds_cont_tgt_snapshot_notify_co_ops` register collective RPC aggregators for target fanout responses.
- The `X` macro materializes `struct daos_rpc_handler` arrays for v8 and v9 from `CONT_PROTO_CLI_RPC_LIST` and `CONT_PROTO_SRV_RPC_LIST`.
- `dsm_tls_init()` and `dsm_tls_fini()` allocate/free a `struct dsm_tls` containing thread-local container child caches and container handle hash tables.
- `cont_module_key`, `cont_metrics`, and `cont_module` describe the server module name, module id, version, protocol formats, handler tables, TLS key, and metric hooks.
- `DEFINE_DS_RPC_PROTOCOL(cont, DAOS_CONT_MODULE)` emits the protocol registration glue.

## Control Flow and Integration
When the DAOS engine loads the container module, `cont_module.sm_init` calls `init`. Protocol version count is two; v8 and v9 formats are registered in `sm_proto_fmt`, with matching handler tables in `sm_handlers`. The handler arrays route client metadata operations to `ds_cont_op_handler`, OID allocation to `ds_cont_oid_alloc_handler`, target collective RPCs to target handlers, and server-side prop-set-by-label to `ds_cont_set_prop_srv_handler`.

Each DAOS server xstream/tag that uses this module invokes `dsm_tls_init`. The created `dt_cont_cache` accelerates target-side container-child lookup, while `dt_cont_hdl_hash` caches container handles. Cleanup reverses both allocations.

## State and Persistence Behavior
This file does not manipulate persistent container metadata directly. It owns process/module lifetime state and per-thread caches. Persistent RDB state is initialized and mutated by functions in `srv_container.c` and related files after this module has registered its handlers.

## Dependencies and Integration Points
`srv.c` depends on DAOS engine/module infrastructure (`daos_srv/daos_engine.h`), metrics, RPC registration, `rpc.h`, and `srv_internal.h`. The handler arrays bind this module to implementations in `srv_container.c` and target/snapshot/OID files. The metrics hooks point to `ds_cont_metrics_alloc`, `ds_cont_metrics_free`, and `ds_cont_metrics_count`.

## Risks and Edge Cases
- Handler tables must match the protocol format arrays exactly. Adding an opcode to `rpc.h` without rebuilding handler tables or implementing handlers will break dispatch.
- TLS initialization is multi-step. A failure after creating `dt_cont_cache` must destroy it before returning, and the code does that explicitly.
- Shutdown ordering can matter if property defaults depend on IV state or vice versa. The current init and fini order should be checked when changing either subsystem.
- `sm_proto_count`, `sm_proto_fmt`, `sm_cli_count`, and `sm_handlers` must stay synchronized when introducing another container protocol version.

## Test Signals
Module load/unload tests, engine startup/shutdown tests, RPC registration smoke tests for v8/v9, and TLS cache leak checks are the main signals. Collective RPC tests for target destroy/query/epoch aggregation/snapshot notify validate that the CoRPC aggregators registered here are reachable.
