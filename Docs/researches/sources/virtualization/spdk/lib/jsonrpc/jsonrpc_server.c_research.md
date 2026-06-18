# File Research: sources/virtualization/spdk/lib/jsonrpc/jsonrpc_server.c

Implements JSON-RPC 2.0 protocol parsing, request object validation, response construction, error response construction, logging, send-buffer growth, and batch request aggregation for SPDK's JSON-RPC server.

Key entry points:
- `jsonrpc_parse_request()` detects a complete JSON value from a streaming receive buffer, copies it into request-owned storage, parses it in place, and dispatches top-level objects or arrays.
- `parse_single_request()` validates `jsonrpc`, `method`, `params`, and `id` fields and calls `jsonrpc_server_handle_request()` or `jsonrpc_server_handle_error()`.
- `spdk_jsonrpc_begin_result()`, `spdk_jsonrpc_end_result()`, `spdk_jsonrpc_send_bool_response()`, `spdk_jsonrpc_send_error_response()`, and `spdk_jsonrpc_send_error_response_fmt()` are the public response helpers.
- `jsonrpc_alloc_request()` and `jsonrpc_free_request()` manage per-request buffers, JSON writer contexts, connection outstanding counters, and queue membership.
- `jsonrpc_process_batch_array()`, `decode_batch_element()`, `jsonrpc_complete_batched_request()`, and `jsonrpc_batch_finalize_and_send()` implement JSON-RPC batch behavior.
- `spdk_jsonrpc_set_log_level()` and `spdk_jsonrpc_set_log_file()` configure request/response logging.

Core mechanics:
- Parsing is two-pass: first `spdk_json_parse()` finds whether a complete JSON value is available and where it ends; the second pass decodes into `request->values` with `SPDK_JSON_PARSE_FLAG_DECODE_IN_PLACE`.
- Request validation accepts JSON-RPC version `"2.0"` when present, requires a string method, accepts `id` only as string/number/null, and allows `params` only as object, array, or null.
- Notifications are represented by a missing or null `id`; `spdk_jsonrpc_end_result()` skips sending a response for those requests.
- Response data is accumulated through `spdk_json_write_begin()` using `jsonrpc_server_write_cb()`, which grows `send_buf` by doubling until `SPDK_JSONRPC_SEND_BUF_SIZE_MAX`.
- Parse errors are treated as unrecoverable on the stream because there is no guaranteed resynchronization point, so `jsonrpc_parse_request()` returns an error after emitting a parse error response.
- Batch requests take ownership of the original receive buffer and JSON value array, allocate individual request objects for each element, and collect non-empty per-item responses into a single JSON array.
- Batch finalization uses an extra completion count to avoid sending the aggregate response before all array elements have been decoded and any synchronous completions have run.

Important invariants:
- A request must explicitly send or skip its response before `jsonrpc_free_request()`; this is enforced by `assert(request->response == NULL)`.
- `begin_response()` asserts `send_len == 0` so callers cannot prepend a second response object onto an existing buffer.
- Batch responses omit notification results and emit no payload when every batch element was a notification.
- `conn->outstanding_requests` is incremented when a request is allocated and decremented only when the request is freed.
- Request and batch send buffers allocate one extra byte so the send path can append a temporary null terminator for logging or debugging.
- Batch aggregation is protected by `batch->lock` because individual requests may complete asynchronously.

Filesystem/block relevance:
- This file is not a filesystem algorithm, but it is SPDK's control-plane protocol core. Storage components such as bdevs, lvols, and keyring modules expose management operations through this request/response machinery.

Notable risks:
- Batch finalization queues a pseudo-request directly on the connection send queue; correctness depends on the connection's outstanding counter and queue cleanup paths treating it consistently with normal requests.
- `jsonrpc_parse_request()` copies `len` bytes but passes the original `size` into the second parse call; this relies on the copied buffer still containing enough bytes or the parser stopping at `end`.
- Logging mutates the request buffer by removing newlines when logging is enabled, which is intentional for backward compatibility but means logged/parsing storage is not strictly immutable text.
