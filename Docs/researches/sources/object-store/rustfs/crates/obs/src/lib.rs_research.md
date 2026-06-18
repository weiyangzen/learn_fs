<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/lib.rs -->
# sources/object-store/rustfs/crates/obs/src/lib.rs

## Purpose
Defines the public boundary for the `rustfs-obs` crate. It wires observability submodules and re-exports the user-facing initialization, config, logging, metrics runtime, schema, cleaner, and telemetry types.

## Important APIs, Types, and Functions
Modules include `cleaner`, `config`, `error`, `global`, `logging`, public `metrics`, and `telemetry`. Re-exports include `init_obs`, `init_obs_with_config`, `OtelConfig`, `AppConfig`, `GlobalError`, `LogCleaner`, logging redaction helpers, metrics schema and runtime controller types, `OtelGuard`, `Recorder`, and `telemetry::dial9`.

## Control Flow
No runtime control flow is implemented. This file only determines what downstream crates can import from `rustfs_obs`.

## State and Persistence
No state here. Global state lives in `global.rs`; telemetry provider lifecycle lives under `telemetry`.

## Dependencies and Integration
This is the integration facade for RustFS services. Consumers can initialize observability, start metrics runtime scheduling, access metric schemas, run log cleanup, and use dial9 runtime telemetry through this crate root.

## Risks
The broad re-export surface couples external callers to many internal metrics runtime types, making refactors more expensive. The private `telemetry` module still exposes selected types and dial9, so public API stability depends on those modules.

## Test Signals
Doc examples in the module comment compile as documentation examples where enabled. Child modules provide most behavioral test coverage.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/lib.rs -->
