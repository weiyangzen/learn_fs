# sources/object-store/rustfs/crates/ecstore/Cargo.toml

Purpose: Cargo manifest for the `rustfs-ecstore` crate, the erasure-coding storage backend for RustFS.

Important configuration: package metadata is inherited from the workspace, with documentation and keywords describing erasure coding storage. The crate disables doctests for the library. Feature `rio-v2` optionally enables `rustfs-rio-v2`; default features are empty. Linux targets add Tokio `io-uring`.

Dependencies: the manifest pulls in the RustFS storage stack (`rustfs-filemeta`, `rustfs-storage-api`, `rustfs-config`, `rustfs-common`, `rustfs-madmin`, replication/S3/KMS/policy crates), async/networking (`tokio`, `tonic`, `hyper`, `reqwest`, AWS SDK), encoding/checksum (`reed-solomon-erasure`, `reed-solomon-simd`, hashes, base64), observability (`tracing`, OpenTelemetry, metrics), persistence helpers, and cloud clients. Build dependency `shadow-rs` supplies build metadata used by admin server info.

Integration points: declares four Criterion benchmarks: erasure, comparison, rename data/meta, and single-block non-inline. Dev dependencies include Criterion, Tokio test utilities, tracing subscriber, and serial tests.

State and persistence behavior: not runtime code, but it controls compiled feature surfaces and benchmark availability.

Risks: broad dependency surface makes feature resolution and workspace version compatibility important. Optional `rio-v2` and target-specific `io-uring` can create platform-specific behavior.

Test signals: benchmark declarations and dev dependencies show performance-sensitive erasure code and metadata paths are expected to be measured outside normal tests.
