# sources/storage-engines/tikv/components/tikv_util/Cargo.toml

Purpose: defines the `tikv_util` crate package metadata, feature flags, dependencies, Linux-specific dependencies, dev dependencies, and the `channel` benchmark target.

Important APIs/types/functions: as a manifest, it exposes Cargo features rather than Rust APIs. Features are `failpoints = ["fail/failpoints"]` and `test-cgroup = []`. The bench target is named `channel`, uses `benches/channel/mod.rs`, and runs with `test = true` to enable the unstable bench harness.

Control flow: Cargo resolves workspace dependencies and feature flags from this manifest. The Linux target section conditionally includes process and page-size inspection crates. The manifest sets edition `2024`, `publish = false`, and Apache-2.0 licensing.

State and persistence: no runtime persistence. It controls crate composition and build graph state. Many dependencies are workspace-pinned, while some are direct crates or a pinned git revision for `procinfo`.

Dependencies and integration: `tikv_util` is broad infrastructure: async/rate limiting, logging, protobuf/grpc, metrics, serialization, system info, Tokio/YATP execution, tracker, allocation, and TiKV workspace crates. The manifest is consumed by all crate modules under `components/tikv_util`.

Risks: the crate has a large dependency surface, so feature unification and build time are important. The git dependency is a reproducibility risk if unavailable despite the pinned revision. Enabling full Tokio plus multiple legacy async crates can increase compatibility complexity.

Test signals: dev dependencies support local tests; the channel benchmark validates mpsc performance surfaces when run with nightly bench support.
