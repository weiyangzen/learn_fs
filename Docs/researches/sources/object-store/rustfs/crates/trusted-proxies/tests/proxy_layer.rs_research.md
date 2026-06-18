# sources/object-store/rustfs/crates/trusted-proxies/tests/proxy_layer.rs

Purpose: Standalone Tower tests for the default simplified `TrustedProxyLayer`.

Important APIs tested: `TrustedProxyLayer::enabled().layer(service)`, request extension insertion of peer `SocketAddr`, and downstream access to `ClientInfo`.

Control flow: The first test inserts an internal peer (`10.0.0.5`) with XFF and expects response body to be forwarded client IP. The second inserts a public peer (`8.8.8.8`) with XFF and expects the direct peer IP, proving forwarded headers are ignored from non-internal peers.

State and dependencies: Uses Axum body/request/response types, Tower `service_fn`, `Layer`, and `ServiceExt`.

Integration points: Exercises the crate's default public layer rather than legacy aliases.

Risks and coverage gaps: Tests only XFF, not X-Real-IP/RFC7239/host/proto behavior or disabled layer. It confirms the core security boundary of simple mode: only internal peers can override client IP.
