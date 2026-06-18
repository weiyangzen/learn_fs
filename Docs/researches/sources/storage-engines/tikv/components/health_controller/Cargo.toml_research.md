<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/health_controller/Cargo.toml -->
# sources/storage-engines/tikv/components/health_controller/Cargo.toml

Purpose: this manifest defines the `health_controller` crate, a non-published TiKV component for health reporting/control-plane integration.

Important build surface: the crate is Rust 2021, Apache-2.0 licensed, version `0.1.0`, and depends on workspace crates for collections, `grpcio-health`, `kvproto`, logging, and TiKV utilities. It also uses `ordered-float`, `parking_lot`, and `prometheus`.

Dependencies and integration points: `grpcio-health` indicates integration with gRPC health services; `kvproto` provides TiKV protobuf types; `prometheus` supports health metrics; `slog`/`slog-global` support logging. The manifest does not define extra binaries or features in this file.

State and persistence behavior: the manifest has no runtime state. It declares dependencies for an in-process health controller rather than storage persistence.

Risks: because only the manifest is in scope here, behavioral risks in health scoring or service transitions must be researched from source files outside this work item. Dependency choices suggest concurrency through `parking_lot` and floating-point ordering through `ordered-float`, both of which can matter for health calculations.

Test signals: no tests or dev-dependencies are declared in this manifest. Test coverage must come from crate source modules or workspace-level tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/health_controller/Cargo.toml -->
