## sources/storage-engines/tikv/components/server/Cargo.toml

Purpose: package manifest for the `server` component crate that assembles TiKV runtime services.

Important APIs/types/functions: declares package `server`, edition 2024, features forwarding allocator, failpoint, engine, backup stream, and test-engine options. Dependencies include core storage engines, raftstore, resource_metering, security, PD client, CDC, backup, grpcio, tikv, tokio, yatp, and many support crates.

Control flow: no runtime control flow; manifest features decide compile-time capabilities such as allocator selection, memory engine, failpoints, and raft/rocks test engines.

State/persistence: no direct state; dependency choices govern access to RocksDB, raft log engine, encryption, backup, and server modules that persist data.

Dependencies/integration: this crate is an integration hub. The manifest explicitly depends on both `resource_metering` and `security`, matching the server startup code that wires metering and TLS into grpc/storage.

Risks: broad dependency surface means feature mismatches can affect large runtime areas. Edition 2024 may require workspace/toolchain support.

Test signals: features expose test engine configurations and failpoints; individual source files contain targeted unit tests for disk usage, raft engine switching, and compaction pressure.
