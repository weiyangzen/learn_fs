# sources/object-store/daos/src/engine/drpc_internal.h

## Purpose
Collects private dRPC declarations shared by the engine listener, progress loop, client, and RAS code. It defines the listener socket path, progress/session/call context structures, lifecycle APIs, generic client init/fini, and readiness notification hook.

## Important APIs and types
- `drpc_listener_socket_path` is the engine listener UNIX socket path advertised to daos_server.
- `struct drpc_progress_context` holds the listener context and a linked list of session contexts.
- `struct drpc_call_ctx` bundles a session, incoming call, and response for asynchronous handler ULT execution.
- `struct drpc_list` links active dRPC sessions.
- `drpc_progress_context_create/close()` manage listener/session context lifetime.
- `drpc_progress()` polls listener and sessions.
- `drpc_listener_init/fini()` start/stop the listener ULT.
- `drpc_init/fini()` manage the client path to daos_server.
- `drpc_notify_ready()` tells daos_server the engine is ready.

## Control flow and integration
`drpc_listener_init()` creates a socket path and progress context, `drpc_progress()` accepts sessions and spawns handler ULTs, and `drpc_listener_fini()` stops and closes the context. Client-side code initializes its separate server socket path with `drpc_init()` and uses `dss_drpc_call()` declared elsewhere. RAS uses the client path and generated event protobufs.

## State and persistence behavior
All state is process-local and socket/file-descriptor based. There is no persistent storage; the socket path is a runtime artifact under `dss_socket_dir`.

## Dependencies
Includes dRPC API, GURT list, and RAS server header. It is included by all engine dRPC implementation files in this subset.

## Risks
The structures expose raw `struct drpc *` pointers with ownership comments saying they are pointers, not copies. Correct ref-counting and close ordering are therefore critical. Listener socket path is global and must be initialized before readiness notification and freed after listener shutdown.

## Test signals
Existing listener/progress/client tests cover most declared behavior. Additional tests should verify startup/fini ordering, null/invalid progress contexts, and readiness notification after listener path generation.
