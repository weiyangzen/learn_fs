# sources/object-store/rustfs/crates/trusted-proxies/src/middleware/service.rs

Purpose: Legacy Tower `Service` wrapper that validates proxy headers and inserts `ClientInfo` into request extensions.

Important APIs/state: `TrustedProxyMiddleware<S>` stores inner service, `Arc<ProxyValidator>`, and enabled flag. Constructors `new` and `from_layer`; implements `Service<Request<ReqBody>>`.

Control flow: Disabled mode passes through. Enabled mode reads peer `SocketAddr` from request extensions, calls `validate_request`, inserts successful `ClientInfo`, falls back to direct peer for recoverable errors, and logs non-recoverable validation failures without inserting replacement info. It always forwards the request to the inner service.

Dependencies and integration: Uses `http::Request`, Tower, `ClientInfo`, `ProxyValidator`, and tracing. Relies on upstream server layers to populate `SocketAddr` in request extensions.

Risks and tests: Non-recoverable validation errors still allow request processing and may leave no `ClientInfo`, which can surprise downstream code expecting it. Missing peer address falls back to `0.0.0.0:0`. Integration tests cover pass-through success but not error insertion semantics.
