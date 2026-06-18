# sources/object-store/rustfs/crates/trusted-proxies/tests/integration/proxy_tests.rs

Purpose: Axum/Tower integration smoke test for the legacy trusted proxy layer.

Important APIs tested: `TrustedProxyConfig::new`, `TrustedProxy::Single`, `ValidationMode::HopByHop`, `LegacyTrustedProxyLayer::enabled`, Axum router layering, and `tower::ServiceExt::oneshot`.

Control flow: Builds a route returning `OK`, layers the legacy proxy layer, sends a request with `X-Forwarded-For`, and asserts HTTP 200.

State and dependencies: Async Tokio test with no external state. It does not insert peer `SocketAddr` into request extensions, so validator follows missing-peer direct fallback.

Integration points: Confirms the legacy layer composes with Axum and does not reject requests.

Risks and coverage gaps: It does not assert inserted `ClientInfo`, trusted proxy behavior, header parsing, or error fallback. Because peer address is missing, it does not fully exercise trusted proxy validation.
