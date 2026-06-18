# sources/object-store/rustfs/crates/keystone/src/middleware.rs

## Purpose
`middleware.rs` implements Tower middleware that intercepts HTTP requests with Keystone token headers, validates them, and exposes resulting RustFS credentials through task-local storage for downstream request handlers.

## Important APIs, Types, and Functions
`KEYSTONE_CREDENTIALS` is a Tokio task-local `Option<Credentials>`. `KeystoneAuthLayer` is a Tower `Layer` holding an optional `Arc<KeystoneAuthProvider>`. `KeystoneAuthMiddleware<S>` implements `Service<Request<Incoming>>` and returns responses with an erased `UnsyncBoxBody`. Helpers include `extract_keystone_token`, which reads `X-Auth-Token`, and `xml_escape`, which escapes XML error details.

## Control Flow
If no provider is configured, the middleware passes the request through unchanged except for body boxing. If a provider exists, it checks `X-Auth-Token`. With a token, it calls `authenticate_with_token`; success scopes `KEYSTONE_CREDENTIALS` to `Some(credentials)` while calling the inner service. Failure returns an immediate 401 XML response with `WWW-Authenticate: Keystone`. If no token is present, the request passes through to normal S3 authentication.

## State and Persistence Behavior
State is request-scoped via Tokio task-local storage and provider-scoped via the provider's caches. No middleware state is persisted. The task-local scope ends after the inner service future resolves.

## Dependencies and Integration Points
The middleware depends on Hyper request bodies, HTTP response/status types, Tower `Layer`/`Service`, `http-body-util` for body conversion, and `rustfs_credentials::Credentials`. It integrates with upstream HTTP routing and downstream auth handlers that call `KEYSTONE_CREDENTIALS.try_with`.

## Risks and Edge Cases
Only `X-Auth-Token` is supported; Swift's `X-Storage-Token` is explicitly deferred. A malformed header value is ignored because `to_str().ok()` returns `None`, causing fallback to S3 auth rather than a 400/401. When Keystone auth fails, fallback is intentionally disabled. XML error details include the display string from the error after escaping; this can reveal operational details. The middleware clones `inner` per call, which is standard Tower practice only if the wrapped service is clone-safe for concurrent use.

## Test Signals
Unit tests cover layer construction, header extraction, XML escaping, and task-local scope behavior. Comments state valid/invalid token tests require a mock Keystone server and are not yet implemented. Integration tests also focus on task-local behavior rather than live middleware HTTP calls.
