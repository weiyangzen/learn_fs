# sources/object-store/daos/src/engine/drpc_progress.c

## Purpose
Implements the polling/progress loop for the engine dRPC listener. It multiplexes the listener socket and active session sockets, accepts new connections, receives calls, creates responses, dispatches handlers in ULTs, and cleans up failed/disconnected sessions.

## Important APIs and functions
- `drpc_progress_context_create()` validates a listener and initializes the session list.
- `drpc_progress_context_close()` closes all sessions, closes the listener, and frees context memory.
- `drpc_progress()` is the exported poll/progress entry point.
- Internal helpers map poll events to activity, convert progress contexts to poll arrays, accept listener connections, create/free call contexts, spawn handler ULTs, and process session/listener activity.

## Control flow
`drpc_progress()` validates the context, builds an array of `unixcomm_poll` entries for every session plus the listener, calls `poll()`, and if activity exists, processes sessions first and listener second. Session `POLLIN` calls `handle_incoming_call()`, which receives a `Drpc__Call`, creates a response even for protocol errors, sends failed-unmarshal responses inline, or creates a `drpc_call_ctx` and hands ownership to a handler ULT on `DSS_XS_SYS`. Handler ULTs call `session->handler`, send the response, then free call, response, and session ref. Session errors/hangups destroy the session node. Listener `POLLIN` accepts a new session and adds it to the list.

## State and persistence behavior
All state is volatile: file descriptors inside `struct drpc`, linked session nodes, and in-flight call contexts. The function closes sessions on failures to prevent dead descriptors lingering.

## Dependencies and integration
Depends on POSIX `poll`, dRPC context/session APIs, Argobots yield through session callbacks, DAOS ULT creation, GURT lists, and the listener-installed handler callback. It is driven by `drpc_listener.c` and exercised by the engine dRPC tests.

## Risks
The poll array is a variable-length stack array in `unixcomm_poll()` sized by active session count; very high session counts could pressure stack. `get_open_drpc_session_count()` uses `drpc_is_valid_listener()` for sessions, which is semantically surprising but likely matches dRPC listener/session representation. Processing sessions before the listener means new accepts can be delayed by heavy session churn. If ULT creation fails after adding a session ref, `free_call_ctx()` must correctly drop that ref.

## Test signals
`drpc_progress_tests.c` has strong coverage: invalid contexts, timeout and poll failures, accept failure, valid/bad calls, session cleanup on recv failure/no data/POLLERR/POLLHUP/ULT failure, listener POLLERR/POLLHUP, and context close variants. Additional stress tests could cover many simultaneous sessions and back-to-back calls.
