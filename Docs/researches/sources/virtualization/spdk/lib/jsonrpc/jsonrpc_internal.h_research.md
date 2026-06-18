# File Research: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_internal.h

Full-file read: 196 lines.

This internal header defines JSON-RPC server/client buffers, state structures, limits, and internal function declarations.

Main contents:
- Buffer and limit constants: receive size, send initial/max size, ID max, max connections, max JSON values.
- `struct spdk_jsonrpc_request`: server-side request with connection, copied ID token, send/receive buffers, parsed values, write context, optional batch pointer, and queue link.
- `struct spdk_jsonrpc_batch_request`: batch aggregation state, spinlock, completion counts, response buffer, and original parse buffers.
- `struct spdk_jsonrpc_server_conn`: socket, closed flag, receive buffer, outstanding count, queue lock, send/outstanding queues, close callback, and list link.
- `struct spdk_jsonrpc_server`: listener socket, handler callback, free/active connection queues, and fixed connection array.
- `struct spdk_jsonrpc_client_request`, `spdk_jsonrpc_client_response_internal`, and `spdk_jsonrpc_client`.
- Internal declarations for server request handling, completion, batch cleanup, and client response parsing.

Integration points:
- Shared by JSON-RPC client/server implementation files.
- Encodes ownership expectations for buffers and parsed token lifetimes.

Risks and review notes:
- Fixed server connection cap is 64.
- Server receive buffer is fixed at 256 KiB, while client receive buffer can grow much larger.
- Batch completion uses a spinlock because handlers may complete from different threads.
- Comments distinguish functions that must run only on the server poll thread.

Testing focus:
- Concurrent batch completion.
- Shutdown with incomplete outstanding requests.
- Buffer-limit behavior for large requests/responses.
