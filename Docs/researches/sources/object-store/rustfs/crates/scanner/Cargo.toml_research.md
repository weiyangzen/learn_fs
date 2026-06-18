# sources/object-store/rustfs/crates/scanner/Cargo.toml

## Purpose
This manifest defines the RustFS `rustfs-scanner` crate, which scans buckets/objects and manages lifecycle/data-usage related background scanning.

## Important APIs, Types, And Functions
Package metadata declares workspace versioning, crate name, description, keywords, categories, docs URL, and disabled doctests. Dependencies include RustFS config, ecstore, filemeta, notifications, objectlock, observability, policy, utils, workers, common/runtime crates, plus `async-trait`, `chrono`, `tokio`, `tracing`, `serde`, `serde_json`, `uuid`, and `snafu`.

## Control Flow
Cargo uses the dependency set to compile the scanner crate and its tests. The manifest links scanner code to storage, lifecycle, object-lock, notification, observability, and worker subsystems.

## State And Persistence Behavior
The manifest has no runtime state. It indicates that scanner runtime code can interact with persistent object metadata and lifecycle state through its dependencies.

## Dependencies And Integration Points
The crate is tightly integrated with RustFS object-store internals (`ecstore`, `filemeta`), policy/object-lock/lifecycle subsystems, notification and observability crates, and async runtime infrastructure.

## Risks And Edge Cases
Scanner depends on many internal crates, so version or API changes in storage metadata, lifecycle, or worker crates can break it. Disabled doctests mean examples are not automatically checked.

## Test Signals
The manifest points to the scanner crate test suite, including lifecycle integration tests in the crate tree, but no tests are defined in the manifest itself.
