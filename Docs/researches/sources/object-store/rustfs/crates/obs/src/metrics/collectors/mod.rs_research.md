# sources/object-store/rustfs/crates/obs/src/metrics/collectors/mod.rs

Purpose: declares and re-exports all metrics collector modules and their public DTOs/functions, forming the main collector facade for `crate::metrics`.

Important APIs/types: module declarations include audit, bucket, bucket replication, cluster, cluster config, erasure set, health, IAM, usage, dial9, ILM, node, notification, notification target, replication, request, resource, scanner, CPU/drive/memory/network/process collectors, and feature-gated GPU. Re-exports expose each collector's stats type and collection function.

Control flow: compile-time module wiring only. `system_gpu` is included and re-exported under `#[cfg(feature = "gpu")]`.

State/persistence: no runtime state.

Dependencies/integration: `metrics/mod.rs` re-exports `collectors::*`, and `scheduler.rs` imports most collector functions/types through this facade. This file is the compatibility surface for code that expects `rustfs_obs::metrics::collectors::X` or `rustfs_obs::metrics::X`.

Risks: missing a re-export can make an implemented collector inaccessible to the scheduler or downstream crates. Feature-gated GPU paths must stay symmetric between `mod` declaration and `pub use`. Broad facade exports can preserve old APIs but also expand compile dependencies.

Test signals: no local tests; compile-time coverage comes from modules importing exported collector symbols, especially `scheduler.rs`.
