# File Research: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_server_tcp.c

Implements the TCP/socket side of SPDK's JSON-RPC server: listening, accepting fixed-pool connections, polling receives and sends, queuing responses, handling close callbacks, and shutting the server down.

Key entry points:
- `spdk_jsonrpc_server_listen()` allocates a server, initializes the free connection pool, creates a nonblocking close-on-exec stream socket, binds, and listens.
- `spdk_jsonrpc_server_poll()` is the main progress loop for accepting new connections, sending queued responses, receiving new request bytes, and removing fully closed connections.
- `jsonrpc_server_conn_recv()` receives bytes into the connection buffer and repeatedly calls `jsonrpc_parse_request()` until no full request remains.
- `jsonrpc_server_send_response()` moves a completed request from the outstanding queue to the send queue.
- `jsonrpc_server_conn_send()` drains queued response buffers through `send()` and frees requests after their full payload is written.
- `spdk_jsonrpc_conn_add_close_cb()` and `spdk_jsonrpc_conn_del_close_cb()` install or remove a single connection-close callback.
- `spdk_jsonrpc_server_shutdown()` closes the listen socket and all active connections.

Core mechanics:
- The server keeps a fixed array of `SPDK_JSONRPC_MAX_CONNS` connection objects, split between `free_conns` and active `conns`.
- Accepted sockets are made nonblocking, receive/send queues are initialized, and a per-connection spin lock protects request queues and callback state.
- Receive parsing supports multiple JSON values in one socket read by advancing `offset` by the byte count returned from `jsonrpc_parse_request()` and compacting leftover bytes with `memmove()`.
- Send progress uses `conn->send_request` as the currently partially written response and a `send_offset` plus shrinking `send_len` to handle short writes.
- Connection close marks all outstanding requests' `conn` pointers as `NULL`; batched requests also have their batch connection nulled so later completions skip sending.
- Closed sockets are removed only after `outstanding_requests` reaches zero, allowing asynchronous request handlers to complete and free their requests safely.

Important invariants:
- `send_queue` and `outstanding_queue` are protected by `conn->queue_lock`.
- A response is queued only if the connection is not already marked closed.
- `jsonrpc_server_conn_remove()` asserts `send_queue` is empty after cleanup and before returning the object to the free pool.
- `spdk_jsonrpc_server_poll()` sends before receiving on each connection, which lets already completed responses make progress even if the peer stops sending new input.
- Parse failure closes the connection because stream resynchronization is not guaranteed.

Filesystem/block relevance:
- This file is the network transport for SPDK's JSON-RPC management plane. It carries configuration and runtime control commands for storage subsystems but does not implement block or filesystem state itself.

Notable risks:
- `jsonrpc_server_accept()` uses `accept()` rather than `accept4()`, so close-on-exec is applied to the listen socket but not explicitly to accepted sockets in this file.
- `spdk_jsonrpc_server_shutdown()` frees the server immediately after closing connections; callers must ensure no asynchronous users retain the server object.
- Close callbacks are single-slot only; attempts to register a second distinct callback return `-ENOSPC`.
