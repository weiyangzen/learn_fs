# sources/object-store/rustfs/crates/trusted-proxies/src/simple.rs

Purpose: Default simplified trusted-proxy implementation for RustFS, with an env switch to use the legacy full validator.

Important APIs/state: `TrustedProxyImplementation::{Simple, Legacy}`, global `init`, `is_enabled`, `implementation`, `layer`, public enum `TrustedProxyLayer`, public enum `TrustedProxyMiddleware`, `SimpleTrustedProxyLayer`, and `SimpleTrustedProxyMiddleware`. State uses `OnceLock` for enabled, implementation, and layer.

Control flow: `build_layer` returns disabled simple layer when globally disabled, simple layer by default, or initializes/wraps legacy global layer when env selects legacy/full. Simple middleware reads peer `SocketAddr`, trusts forwarded headers only when the peer IP is internal (private, loopback, or link-local), chooses client IP from XFF, X-Real-IP, or Forwarded, sanitizes host/proto, and inserts `ClientInfo`.

State and dependencies: No persistent dynamic state beyond once-only globals. Depends on Tower, Axum HTTP, `rustfs_config` env defaults, `rustfs_utils`, and legacy types.

Integration points: Re-exported as the crate's default `TrustedProxyLayer`/`init`/`layer`. Tests cover implementation parsing, header priority/fallback, host/proto preservation and sanitization, public-peer rejection of forwarded headers, missing peer behavior, token parsing, internal IP detection, and env-selected legacy mode.

Risks: The simplified model treats all internal peers as trusted proxies, which is pragmatic for internal deployments but risky if untrusted clients can connect from private/link-local networks. `OnceLock` makes env changes after first access ineffective. Host validation rejects whitespace/control but not all authority syntax edge cases.
