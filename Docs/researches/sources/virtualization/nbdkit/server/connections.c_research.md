# File Research: sources/virtualization/nbdkit/server/connections.c

Purpose: Implements per-client connection lifetime, request processing, worker-thread dispatch, connection status transitions, and raw transport I/O for the nbdkit server.

Key structures and state:
- Allocates and owns `struct connection`, declared in `internal.h`.
- Initializes per-connection mutexes: `request_lock`, `read_lock`, `write_lock`, `status_lock`.
- Tracks connection state through `conn_status`: `STATUS_ACTIVE`, `STATUS_SHUTDOWN`, `STATUS_CLIENT_DONE`, `STATUS_DEAD`.
- Creates `default_exportname` storage indexed by backend chain position.
- Optional `status_pipe` lets worker threads wake poll loops when status drops.

Main flow:
- `handle_single_connection(sockin, sockout)` locks connection admission according to the thread model, allocates a connection, runs `top->preconnect`, starts the handshake timeout, performs `protocol_handshake`, then serves requests.
- If the effective thread model is not parallel or only one worker is requested, request processing runs serially in the connection thread.
- Otherwise a worker pool handles `protocol_recv_request_send_reply()` until global quit or connection status reaches client-done/dead.
- On request-processing failure, workers acquire `write_lock` and call `conn->close(SHUT_WR)` to stop writes.
- Before freeing, it calls `backend_finalize(conn->top_context)` under `lock_request`.

Concurrency details:
- `connection_get_status` and `connection_set_status` lock `status_lock` only when workers exist.
- `connection_set_status` only moves status toward lower-severity enum values, and returns true when the caller should initiate shutdown.
- Worker thread names are derived from plugin name plus worker index, and thread-local connection/name state is set per worker.

I/O behavior:
- `raw_recv` reads exactly the requested length, returning `1` for complete read, `0` for EOF before any bytes, and `-1` for errors or partial-record EOF.
- `raw_send_socket` uses `send`, optionally with `MSG_MORE` when `SEND_MORE` is requested.
- `raw_send_other` uses `write` for non-socket outputs on Unix, supporting stdin/stdout-style operation and fuzzing.
- `raw_close` handles half-close versus full close, with separate sockin/sockout support.

Dependencies:
- Calls protocol entry points from handshake and request processing modules.
- Calls backend lifecycle functions and lock helpers from `backend.c`/`locks.c`.
- Uses thread-local APIs for current connection and server thread identity.
- Uses platform socket wrappers from `windows-compat.h`.

Important edge cases:
- If `top` is already null during async shutdown, a new connection returns immediately.
- If atomic `pipe2` is unavailable, pipe setup is serialized under `lock_request` and constrained by thread model.
- `free_connection` avoids calling plugin close paths after global quit, because unload may already be in progress.
