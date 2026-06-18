# sources/object-store/rustfs/crates/trusted-proxies/src/utils/mod.rs

Purpose: Utility module aggregator for trusted-proxies.

Important APIs: Declares `ip` and `validation`, then publicly re-exports both.

Control flow and state: Compile-time wiring only. It exposes `IpUtils`, `ValidationUtils`, and free helper functions through `crate::utils` and crate root.

Dependencies and integration: Re-exported by `lib.rs`; validator/chain code and tests import helpers through crate-level paths.

Risks and tests: No runtime risk. Unit tests for IP and validation utilities indirectly confirm the exports.
