<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/Cargo.toml -->
# sources/storage-engines/tikv/components/engine_tirocks/Cargo.toml

## Purpose
This manifest defines `engine_tirocks`, an experimental TiKV engine implementation backed by the `tirocks` Rust bindings. The crate is intended to eventually replace `engine_rocks` once feature parity is reached.

## Important APIs, Types, and Functions
Dependencies include `engine_traits`, `tirocks` from the `busyjay/tirocks` dev branch, TiKV key/API/version crates, metrics/logging crates, tracker, transaction types, and `tikv_alloc`. Dev dependencies include `kvproto`, `rand`, and `tempfile`.

## Control Flow
Cargo resolves the external `tirocks` git dependency and workspace dependencies. Runtime behavior is implemented in `src/lib.rs` modules.

## State and Persistence Behavior
No state is stored in the manifest. The selected `tirocks` dependency controls on-disk RocksDB compatibility and API surface for the crate.

## Dependencies and Integration Points
The git branch dependency is the highest-risk integration point because API and behavior can move outside crates.io versioning. The crate also integrates with TiKV metrics/tracker systems through `perf_context.rs`.

## Risks and Edge Cases
Using a git branch can make builds sensitive to remote branch changes unless the workspace lockfile pins a revision. The crate exposes partial engine-trait coverage, with TODOs and panics in source files, so enabling it broadly requires careful feature gating.

## Test Signals
Build and unit tests for `engine_tirocks` validate current tirocks API compatibility. Lockfile checks are important for reproducibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/Cargo.toml -->
