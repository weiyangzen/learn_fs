# File Research: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_client.c

Full-file read: 296 lines.

This file implements JSON-RPC client-side protocol serialization and response parsing, independent of socket transport.

Main responsibilities:
- Decode JSON-RPC 2.0 responses into `spdk_jsonrpc_client_response`.
- Handle single responses and simplified batch responses.
- Build JSON-RPC request objects and request batches into a send buffer.
- Grow request send buffers up to `SPDK_JSONRPC_SEND_BUF_SIZE_MAX`.

Important control flow:
- `jsonrpc_parse_response` first parses without token storage to detect complete JSON and token count, then reparses with in-place decode into owned response storage.
- Batch responses are decoded as arrays; the first error is preserved, otherwise the first result is retained because current use only needs batch success/failure.
- `spdk_jsonrpc_begin_request` writes `jsonrpc`, optional `id`, and optional `method`.
- Single requests finalize immediately and append newline; batch requests share a write context until `spdk_jsonrpc_end_batch`.

Integration points:
- Transport code in `jsonrpc_client_tcp.c` owns sockets and calls `jsonrpc_parse_response`.
- Uses SPDK JSON parser/writer/util APIs.

Risks and review notes:
- Simplified batch response handling discards most individual responses.
- Client supports string or numeric response IDs, but request builder writes integer IDs.
- Only one parsed response can be pending in `client->resp`; another response before retrieval returns `-ENOSPC`.

Testing focus:
- Incomplete streaming response parse.
- Parse errors and oversized token counts.
- Batch success, batch with first/late error, and all-notification-like edge cases.
- Send buffer growth and maximum limit.
