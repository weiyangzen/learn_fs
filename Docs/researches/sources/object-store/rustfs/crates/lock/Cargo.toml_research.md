# sources/object-store/rustfs/crates/lock/Cargo.toml

## Purpose
Declares the `rustfs-lock` crate metadata, workspace inheritance, lint participation, dependencies, and library doctest setting.

## Important APIs, Types, And Functions
This is manifest-only. The package describes distributed locking for RustFS and advertises locking/asynchronous/distributed keywords. It disables doctests for the library.

## Control Flow
No runtime control flow.

## State And Persistence
No state. It controls build-time dependency resolution through workspace dependency entries.

## Dependencies And Integration
Runtime dependencies include RustFS IO metrics and utils, async/futures, serde/JSON, Tokio, tonic, tracing, uuid, thiserror, parking_lot, smallvec, smartstring, and crossbeam-queue. Workspace lints apply to the crate.

## Risks And Edge Cases
No feature flags are declared here despite source comments mentioning lock enablement through environment variables. Remote lock support is not exposed as a feature in this manifest.

## Test Signals
The manifest disables doctests; regular unit/integration tests are controlled by Rust source modules and workspace test commands.
