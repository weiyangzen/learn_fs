# sources/object-store/rustfs/crates/trusted-proxies/src/config/mod.rs

Purpose: Public configuration module boundary.

Important APIs: Declares `env`, `loader`, and `types`, then publicly re-exports all three.

Control flow and state: Compile-time wiring only. It centralizes env helpers, `ConfigLoader`, and configuration structs/enums under `crate::config` and crate-level re-exports.

Dependencies and integration: `lib.rs` re-exports this module, so downstream users can access config types directly from `rustfs_trusted_proxies`. Most trusted-proxies modules import these public config types through crate re-exports.

Risks and tests: Wildcard re-export broadens public API. Unit config tests import `ConfigLoader`, `TrustedProxy`, `TrustedProxyConfig`, and `ValidationMode` via the crate, indirectly confirming this module exports the expected items.
