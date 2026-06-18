# sources/object-store/daos/src/engine/drpc_listener.c

## Purpose
Starts, runs, and tears down the engine's dRPC listener ULT. The listener exposes a per-engine UNIX-domain socket used by local daos_server/control-plane clients to send dRPC calls into the engine.

## Important APIs and functions
- `drpc_listener_init()` generates socket path, initializes status mutex, and starts the listener ULT.
- `drpc_listener_fini()` stops the listener, joins/frees the ULT, frees the mutex, and frees the socket path.
- `drpc_listener_run()` loops on `drpc_progress()` until stopped.
- `setup_listener_ctx()` unlinks any stale socket path, calls `drpc_listen()`, and wraps it in a progress context.
- `generate_socket_path()` formats `dss_socket_dir/daos_engine_<pid>.sock`.

## Control flow
Initialization creates `status.running_mutex`, calls `setup_listener_ctx()`, and creates a ULT on `DSS_XS_DRPC`. The ULT marks itself running and repeatedly calls `drpc_progress(ctx, 1000)`, logging all errors except timeout, then yields. Finalization sets running false, joins the thread, frees Argobots resources, and frees `drpc_listener_socket_path`. The progress context closes listener/session dRPC contexts from inside the listener ULT when the loop exits.

## State and persistence behavior
Runtime state is the static `status` struct and global socket path. The socket file is unlinked before listen setup to clear stale entries; no DAOS persistent state is touched.

## Dependencies and integration
Depends on Argobots, engine ULT creation, `drpc_hdlr_process_msg()` as the callback, `drpc_progress_context_create/close()`, and `dss_socket_dir`. `drpc_client.c` includes the listener path in readiness notification.

## Risks
If `ABT_mutex_create()` fails after socket path allocation, the path is not freed in `drpc_listener_init()`. `drpc_listener_fini()` assumes init/start succeeded enough for `status.thread` and mutex to be valid. Unlinking the socket path before listen is practical but can remove a live socket if path generation collides, though PID-based naming should avoid that.

## Test signals
Existing listener tests should validate socket setup, ULT start/stop, progress error handling, stale socket unlink behavior, mutex/thread cleanup, and readiness path visibility. Failure-injection tests should cover listen/progress-context/ULT creation failures.
