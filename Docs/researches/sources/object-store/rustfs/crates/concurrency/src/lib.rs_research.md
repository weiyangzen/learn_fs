# sources/object-store/rustfs/crates/concurrency/src/lib.rs

## Purpose
Crate root for RustFS concurrency management. It documents the facade architecture, denies missing docs and unsafe code, re-exports core I/O primitives, gates feature modules, and publishes a prelude.

## Important APIs, types, and functions
Public re-exports include `ConcurrencyConfig`, `ConcurrencyFeatures`, `ConcurrencyManager`, `GetObjectQueueSnapshot`, feature-specific managers/guards/policies, and selected `rustfs_io_core` types such as timeout errors, lock stats, backpressure state, scheduler types, and helper functions.

## Control flow
Compile-time `cfg(feature = "...")` declarations decide which modules and exports exist. The prelude mirrors those feature-gated exports plus the top-level manager/config types.

## State and persistence behavior
The crate root has no runtime state; it defines module boundaries and public API surface.

## Dependencies and integration points
This is the integration point between downstream RustFS services and lower-level `rustfs-io-core`/`rustfs-io-metrics`. The `workers` module is always public, while timeout/lock/deadlock/backpressure/scheduler are feature-gated.

## Risks and edge cases
`#![deny(missing_docs)]` makes new public exports fail compilation without docs. `config.rs` imports feature modules directly, so unusual feature sets should be checked. Broad re-exports couple the facade's semver surface to `io-core` types.

## Test signals
No direct tests in this file; compile tests across feature sets and downstream imports are the main signal.
