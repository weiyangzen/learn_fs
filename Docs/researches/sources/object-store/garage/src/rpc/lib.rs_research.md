# sources/object-store/garage/src/rpc/lib.rs

Purpose: crate root for `garage_rpc`.

Important exports: imports `tracing` macros, declares private `metrics` and `system_metrics`, conditionally declares `consul` and `kubernetes`, and publicly exposes `layout`, `replication_mode`, `system`, and `rpc_helper`. It also re-exports `rpc_helper::*`, making common RPC types and helpers available through the crate root.

Control flow: no runtime control flow; this is module wiring.

State and persistence: none directly. Persistence is implemented in the submodules, particularly `layout::manager` and `system`.

Dependencies and integration: ties together the public surface used by `garage_table`, block management, API/admin layers, and cluster startup. Feature gates here must match manifest features and conditional uses in `system.rs`.

Risks and test signals: overly broad `pub use rpc_helper::*` makes helper API changes externally visible. Feature-gated modules must stay synchronized with `Cargo.toml`. No tests in this file; compile coverage across feature combinations is the main signal.
