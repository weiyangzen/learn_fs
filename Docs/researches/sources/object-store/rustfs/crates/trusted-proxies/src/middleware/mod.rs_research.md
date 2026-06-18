# sources/object-store/rustfs/crates/trusted-proxies/src/middleware/mod.rs

Purpose: Middleware module aggregator for the legacy Tower layer and service.

Important APIs: Declares `layer` and `service`, then re-exports both.

Control flow and state: Compile-time namespace wiring only. Exposes `TrustedProxyLayer` and `TrustedProxyMiddleware` from the legacy implementation.

Dependencies and integration: `lib.rs` re-exports these as `LegacyTrustedProxyLayer` and `LegacyTrustedProxyMiddleware` to avoid colliding with simplified defaults.

Risks and tests: No local runtime risk. Integration tests import `LegacyTrustedProxyLayer` through crate root and confirm layer composition compiles and returns HTTP 200.
