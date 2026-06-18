# File Research: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_client_tcp.c

Full-file read: 397 lines.

This file implements the socket transport for the SPDK JSON-RPC client.

Main responsibilities:
- Create nonblocking AF_UNIX or TCP sockets and connect to JSON-RPC servers.
- Poll connecting sockets until `SO_ERROR` confirms connection success.
- Send queued request buffers and free requests after all bytes are written.
- Receive response bytes into a growable buffer, NUL-terminate it, and invoke `jsonrpc_parse_response`.
- Provide client close, request allocation/free, send, poll, response get, and response free APIs.

Important control flow:
- `spdk_jsonrpc_client_connect` parses AF_UNIX paths directly or uses `spdk_parse_ip_addr` plus `getaddrinfo` for TCP; default TCP port is `5260`.
- `spdk_jsonrpc_client_poll` switches between connecting and connected poll paths.
- Connected polling listens for both `POLLIN` and `POLLOUT`; it sends pending request data first, then receives.
- `spdk_jsonrpc_client_get_response` transfers ownership of the internal response object to the caller.

Integration points:
- Uses protocol helpers and structs from `jsonrpc_internal.h`.
- Uses POSIX sockets, `poll`, `getaddrinfo`, and SPDK string/util logging helpers.

Risks and review notes:
- Only one outstanding request buffer is accepted at a time.
- Receive buffer grows by doubling and is bounded by the send-buffer max constant.
- On connect errors after socket creation, sockfd is closed and reset.
- `jsonrpc_client_poll` treats `-EAGAIN` as incomplete-message non-error, though `jsonrpc_parse_response` returns `0` for incomplete in this client implementation.

Testing focus:
- Nonblocking connect success/failure/timeouts.
- Partial send and partial receive.
- AF_UNIX path length rejection.
- Default port parsing and invalid address handling.
