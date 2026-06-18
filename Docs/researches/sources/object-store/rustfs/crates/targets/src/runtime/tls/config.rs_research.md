## sources/object-store/rustfs/crates/targets/src/runtime/tls/config.rs

Purpose: keeps the targets crate on the same TLS reload configuration model as the shared `rustfs_tls_runtime` crate. This file is a compatibility/re-export layer rather than an independent configuration implementation.

Important APIs/types/functions: re-exports `TlsReloadOptions`, `ReloadDetectMode`, and aliases `rustfs_tls_runtime::config::ReloadApplyHint` as `ReloadApplyMode`. The alias preserves target-side naming while tying behavior to the shared runtime type.

Control flow and state: none; all defaults and semantics live in `crates/tls-runtime/src/config.rs`. Default options there enable polling every 15 seconds, debounce for 2 seconds, use a 1 second minimum stable age field, and apply lazily.

Dependencies and integration points: used by target TLS adapter, coordinator, trait, and tests. Because this is a re-export, crate users can import target TLS configuration through the targets crate without depending directly on `rustfs-tls-runtime`.

Risks: the alias can hide the fact that target-side `ReloadApplyMode` is actually a shared `ReloadApplyHint`. Any change to the shared enum is an API change here. There are no local tests because there is no local logic.

Test signals: behavior is indirectly covered by target coordinator and adapter tests that construct `TlsReloadOptions` and match `ReloadApplyMode` variants.
