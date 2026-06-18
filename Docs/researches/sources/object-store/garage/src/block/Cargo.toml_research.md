# sources/object-store/garage/src/block/Cargo.toml

Purpose: declares the `garage_block` Rust crate, described as the block manager for the Garage object store.

Important APIs/types/functions: configures `lib.rs` as the library root and exposes the crate under version `2.3.0`, edition 2018, AGPL-3.0. It defines the `system-libs` feature to pass through `zstd/pkg-config`.

Control flow: build-time only. Cargo resolves workspace dependencies and optional system-library linkage before compiling the block manager.

State and persistence: no runtime state, but dependency choices affect persistence-critical code in the block manager, including database access, RPC, compression, async IO, and metrics.

Dependencies and integration points: workspace crates `garage_db`, `garage_net`, `garage_rpc`, and `garage_util`; third-party crates include `opentelemetry`, `arc-swap`, `async-trait`, `bytes`, `bytesize`, `hex`, `tracing`, `rand`, `async-compression`, `zstd`, `serde`, `futures`, `tokio`, and `tokio-util`.

Risks: feature linkage for zstd must remain compatible with deployment packaging. Because the crate owns on-disk blocks and repair/resync workflows, dependency upgrades can affect data durability, async behavior, and compression interoperability.

Test signals: no direct manifest tests; validation comes from compiling the block crate and exercising block manager, repair, resync, and integration tests in dependent crates.
