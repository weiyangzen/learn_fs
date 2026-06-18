# sources/object-store/daos/src/engine/drpc_client.c

## Purpose
Implements the engine-side dRPC client used to call daos_server/control-plane methods over the server UNIX-domain socket. It also provides management helpers for readiness notification, pool service lookup, pool lookup by label, and pool listing.

## Important APIs
- `drpc_init()` and `drpc_fini()` create/free the `daos_server.sock` path under `dss_socket_dir`.
- `dss_drpc_call()` is the generic dRPC invocation helper.
- `drpc_notify_ready()` sends engine URI, incarnation, dRPC listener socket path, instance index, target count, context count, and check mode.
- `ds_get_pool_svc_ranks()`, `ds_pool_find_bylabel()`, and `ds_get_pool_list()` call server management dRPC methods and convert protobuf responses into DAOS UUID/rank/list structures.

## Control flow
`dss_drpc_call()` builds a stack argument and either invokes `dss_drpc_thread()` inline for no-response/no-scheduler calls or creates a pthread to avoid blocking the current xstream. Scheduled calls obtain an anonymous scheduler request and poll `pthread_tryjoin_np()` with exponential backoff sleeps, then return the thread's DAOS return code. The worker thread opens a private dRPC connection to avoid shared-context concurrency problems, creates a `Drpc__Call`, borrows the caller request buffer as the body, invokes `drpc_call()`, frees/no-returns the response depending on flags, clears borrowed body pointers, closes the connection, and returns.

## State and persistence behavior
Only static state is `dss_drpc_path`. Calls are stateless and use private transient dRPC connections. Returned pool service ranks, labels, and pool lists are heap allocations owned by callers. Readiness notification borrows `drpc_listener_socket_path` from the listener.

## Dependencies and integration
Depends on DAOS engine globals (`dss_socket_dir`, `dss_instance_idx`, `dss_tgt_nr`, context counts), protobuf bindings in `srv.pb-c.h`, dRPC module IDs, scheduler request APIs, pthreads, backoff helpers, UUID/rank conversion helpers, and `drpc_internal.h`. RAS and checker code reuse `dss_drpc_call()`.

## Risks
If `pthread_create()` fails, the code returns without `sched_req_put()`, which appears to leak the scheduler request. The stack argument passed to the pthread is safe only because the caller waits until join; the assert after `pthread_tryjoin_np()` is the safety boundary. No-response calls run inline and can block the current ULT/xstream. Response parsing must treat dRPC status and protobuf response status separately. `drpc_fini()` asserts path initialization.

## Test signals
Existing `drpc_client_tests.c` is the natural test suite. Coverage should include inline/no-response calls, scheduled pthread path, connection/call/pack failures, non-success dRPC statuses, malformed protobuf responses, rank list conversion, pool-list overflow and cleanup, readiness check-mode fields, and the scheduler-request leak path on pthread creation failure.
