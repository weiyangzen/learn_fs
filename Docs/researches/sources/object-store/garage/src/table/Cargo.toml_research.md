# sources/object-store/garage/src/table/Cargo.toml

Purpose: crate manifest for `garage_table`, Garage's table sharding and replication engine.

Important configuration: package version `2.3.0`, edition 2018, AGPL-3.0, `lib.rs` as root. The description says it is a "Table sharding and replication engine (DynamoDB-like) for the Garage object store".

Dependencies: internal crates are `garage_db`, `garage_rpc`, and `garage_util`. External workspace dependencies include OpenTelemetry, `async-trait`, `arc-swap`, `hex`, `hexdump`, `tracing`, `rand`, `serde`, `serde_bytes`, `futures`, `futures-util`, and Tokio. Workspace lints apply.

State and persistence behavior: the manifest itself has none, but dependency choices show the crate owns DB-backed table persistence, RPC sync/GC, background workers, metrics, and async coordination.

Integration points: consumed by Garage table definitions and storage subsystems. It depends on RPC layout and system crates, so table consistency is tightly coupled to cluster membership and layout history.

Risks and test signals: no feature flags here; it always compiles table sync, GC, Merkle, and replication support. API compatibility with `garage_db`, `garage_rpc`, and `garage_util` is critical. Workspace lint changes can affect this crate broadly.
