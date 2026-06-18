# sources/storage-engines/tikv/components/tracker/Cargo.toml

Purpose: Cargo manifest for the private `tracker` crate.

Important APIs/types/functions: declares dependencies on `crossbeam-utils`, `kvproto`, `parking_lot`, `pin-project`, Prometheus, `slab`, `slog`, and supporting macros.

Control flow: build metadata only.

State and persistence: no runtime state; controls compilation and linkage.

Dependencies/integration: tracker bridges request metrics, protobuf response details, TLS propagation, and sharded slab storage.

Risks: dependency changes can affect pin projection, slab behavior, locking, or protobuf field availability.

Test signals: no manifest-local tests.
