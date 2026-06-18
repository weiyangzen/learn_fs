<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/http_reader.rs -->
# sources/object-store/rustfs/crates/rio/src/http_reader.rs

## Purpose
Implements HTTP-backed async read and write adapters for RustFS internode streaming RPCs and other HTTP transfers. It also centralizes reqwest client caching, outbound TLS/mTLS refresh, proxy bypass for loopback, internode metrics, classified errors, and optional read stall timeouts.

## Important APIs, types, and functions
- `HttpReader::new`, `new_with_stall_timeout`, and `with_capacity` issue a request immediately and expose the response body as `AsyncRead`.
- `HttpWriter::new` spawns a background request and exposes the request body as `AsyncWrite`.
- `InternodeHttpErrorKind`, `InternodeHttpRequestContext`, and `InternodeHttpError` classify and carry retryable HTTP/network failures.
- `get_http_client`, `build_http_client`, and `CLIENT_CACHE` manage generation-aware TLS client reuse.
- Metric helpers record outgoing requests, bytes, and classified errors for known `/rustfs/rpc/*` routes.

## Control flow
Client lookup chooses the normal or no-proxy reqwest client based on the URL host and current outbound TLS generation. `HttpReader` sends the request, rejects non-success status codes, wraps `bytes_stream` in `StreamReader`, records received bytes on each read, and resets or fires a stall timer. `HttpWriter` creates an mpsc stream of optional byte chunks, spawns a reqwest request using `Body::wrap_stream`, buffers small writes up to 1 MiB, sends large writes directly, sends `None` on shutdown, and waits for the background task to finish.

## State and persistence behavior
Persistent data is not stored here, but streaming state includes cached TLS clients, request metadata, pending writer chunks, finish state, background task handle, and one-shot error channel. Metrics are emitted to the global internode metrics registry. TLS state is refreshed by generation and stale generations are recorded.

## Dependencies and integration points
Depends on `reqwest`, `tokio`, `tokio-util`, `futures`, `bytes`, `http`, `rustfs_tls_runtime`, `rustfs_io_metrics`, `rustfs_config`, `rustfs_utils`, and `rustls_pki_types`. It integrates with internode read-file, put-file, and walk-dir RPC paths, plus the generic `Writer` enum and reader capability traits.

## Risks and edge cases
Error classification relies partly on reqwest flags and message text, which can change. `HttpWriter::new` reports success before the server response is known; write calls later observe async failures via `err_rx` or shutdown. The mpsc channel and 1 MiB buffer bound memory, but slow receivers can apply backpressure. Loopback proxy bypass is critical for tests and local RPC safety. TLS cache races are guarded, but a stale generation can still be used until detection.

## Test signals
Tests cover route-to-operation mapping, no preflight HEAD/PUT behavior, stall timeout after partial progress, many small writes, vectored writes, request error context, retryability for gateway statuses, DNS error IO kind, status error source/context, test helper retryability, and loopback proxy bypass.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/http_reader.rs -->
