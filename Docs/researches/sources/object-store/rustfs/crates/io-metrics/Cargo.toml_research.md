<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/Cargo.toml -->
## sources/object-store/rustfs/crates/io-metrics/Cargo.toml

### Purpose
Defines the `rustfs-io-metrics` crate metadata, benchmark target, dependencies, dev-dependencies, and workspace lint inheritance.

### Important APIs, Types, And Functions
This manifest exposes a library crate named `rustfs-io-metrics` with description "Metrics collection and reporting for RustFS (using metrics crate + OTEL)". It declares a Criterion benchmark named `metrics_pipeline` with `harness = false`.

### Control Flow
There is no runtime control flow. Build-time behavior pulls versions, edition, license, repository, rust-version, and homepage from the workspace. The benchmark target is discovered by Cargo under `benches/metrics_pipeline.rs`.

### State And Persistence
No runtime state. The manifest controls crate identity and dependency graph.

### Dependencies And Integration Points
Runtime dependencies are workspace `metrics`, `rustfs-s3-ops`, `num_cpus`, `thiserror`, `tokio` with `sync,rt`, `tracing`, and `sysinfo`. Dev dependencies add `criterion` and `tokio` with `test-util,rt,macros`. The dependency set maps directly to crate modules: metrics macros, S3 operation labels, CPU-derived cache sharding defaults, error types, async locks/runtime, autotuner logging, and process sampling.

### Risks
The crate says OTEL in metadata but intentionally delegates exporter initialization to `rustfs-obs`; consumers must install a metrics recorder/exporter elsewhere. Tokio features are intentionally narrow; modules using test runtimes rely on dev features. Any new async functionality may need feature expansion.

### Test Signals
The manifest supports regular unit tests and Criterion benchmark execution. The benchmark target is explicitly configured.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/Cargo.toml -->
