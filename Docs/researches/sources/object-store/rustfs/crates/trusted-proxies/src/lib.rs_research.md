# sources/object-store/rustfs/crates/trusted-proxies/src/lib.rs

Purpose: Crate root for trusted proxy middleware, configuration, cloud helpers, validation, metrics, and utility exports.

Important APIs: Declares modules `cloud`, `config`, `error`, `global`, `middleware`, `proxy`, `simple`, and `utils`. Re-exports all cloud/config/error/proxy/utils items; aliases legacy global functions and middleware types; exports simplified default API from `simple.rs` as `init`, `layer`, `is_enabled`, `implementation`, `TrustedProxyLayer`, and `TrustedProxyMiddleware`.

Control flow and state: No runtime logic; API selection is encoded by re-export names. The public default path is simplified, while legacy names remain available.

Dependencies and integration: Tests import public types through this file, confirming crate-level access. Application users likely layer `TrustedProxyLayer` into Tower/Axum services.

Risks and tests: Having both legacy and simplified `TrustedProxyLayer` names, with aliases for legacy, can confuse users and create migration risk. Compile-time coverage is strong because many tests import through the crate root.
