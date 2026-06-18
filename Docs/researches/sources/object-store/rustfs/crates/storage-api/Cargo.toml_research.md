# sources/object-store/rustfs/crates/storage-api/Cargo.toml

## Purpose
Defines `rustfs-storage-api`, a lightweight contract crate for storage API traits, DTOs, and stable error codes.

## Dependencies and Integration
Runtime dependencies are `async-trait`, `serde`, and `time`. Dev dependencies are `serde_json` and `tokio` with macros/runtime for async trait tests. Doctests are disabled and workspace lints apply.

## Risks and Test Signals
The manifest keeps implementation dependencies out of the API crate, which supports broad reuse. Adding storage backend crates here would increase coupling. Module tests cover async trait usage, DTO serialization/defaults, and error-code round trips.
