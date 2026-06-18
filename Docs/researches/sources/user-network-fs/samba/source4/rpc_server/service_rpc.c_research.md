# sources/user-network-fs/samba/source4/rpc_server/service_rpc.c

## Purpose

This file registers and initializes Samba's `rpc` task service for the source4 DCE/RPC server. It creates the DCE/RPC server context, loads configured endpoint servers, creates the local NCALRPC directory, adds endpoint listeners, and handles the split between endpoints that can run in the normal process model and endpoints that require a single shared process.

## Important APIs, Types, And Functions

`srv_callbacks` supplies DCE/RPC context callbacks for successful authorization logging, GENSEC preparation, root privilege hooks, and association group lookup. The local root hooks are no-ops because this service is already running in the expected server context. `dcesrv_init_endpoints()` iterates `dce_ctx->endpoint_list`, skips unsupported `NCACN_HTTP`, selects either the task's model ops or the `single` process model, and calls `dcesrv_add_ep()` for endpoints whose `use_single_process` flag matches the requested pass.

`dcesrv_task_init()` initializes the RPC server library, sets the task title, creates the DCE/RPC context with callbacks, loads endpoint servers from `dcerpc endpoint servers`, ensures the NCALRPC directory exists, registers multi-process-capable endpoints, and stores the context in `task->private_data`. `dcesrv_post_fork()` runs after worker creation and registers single-process endpoints only for the first instance. `server_service_rpc_init()` registers the service with Samba's task framework.

## Control Flow

Startup enters through `server_service_rpc_init()`, which registers service callbacks. During task initialization, `dcesrv_task_init()` builds the common DCE/RPC context and endpoint list, then calls `dcesrv_init_endpoints(..., false)` to add endpoints that can follow the configured process model. After fork/pre-fork processing, `dcesrv_post_fork()` validates `private_data`, and if `pd->instances == 0`, calls `dcesrv_init_endpoints(..., true)` so shared-context endpoints are added only once. Every post-fork process registers the IRPC name `rpc_server`.

## State And Persistence

The only persistent runtime state owned here is the DCE/RPC context stored in `task->private_data` and registered endpoint listeners. The file may create the NCALRPC directory on disk with mode `0755` if it is missing. It does not persist configuration or endpoint metadata itself; endpoint definitions come from loadparm and endpoint server initialization.

## Dependencies And Integration Points

This service integrates with Samba task services, process models, DCE/RPC server context/endpoint APIs, GENSEC auth setup, DCE/RPC association groups, generated endpoint servers, IRPC messaging, loadparm configuration, NCALRPC filesystem paths, and the process context/event loop supplied by the parent server.

## Risks And Edge Cases

The single-process endpoint split is important for shared policy handles and shared LDB contexts. Registering those endpoints in multiple processes could break handle sharing, while failing to register them in the first instance makes key RPC pipes unavailable. Startup aborts on endpoint initialization errors and NCALRPC directory creation failures. `NCACN_HTTP` endpoints are skipped entirely. The no-op root callbacks assume callers and endpoint implementations do not require privilege transitions from this layer.

## Test Signals

Test signals include successful Samba startup with the `rpc` service enabled, endpoint availability over expected transports except HTTP, creation and permissions of the NCALRPC directory, logs showing no endpoint registration failures, single-process-only endpoints appearing once, multi-process-safe endpoints appearing in normal workers, and successful RPC smoke tests against SAMR, SRVSVC, NETLOGON, and other configured endpoint servers.
