# sources/storage-engines/tikv/components/batch-system/tests/cases/mod.rs

## Purpose
Test module entry point for the batch-system crate.

## APIs, Types, And Functions
Declares `mod batch;` and `mod router;`, making the two test files part of the `tests` target defined in Cargo.toml.

## Control Flow
No runtime logic exists here beyond Rust test discovery through module inclusion.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Connects the Cargo test target to the batch and router test suites. Requires the crate's `test-runner` feature via Cargo target metadata.

## Risks And Test Signals
Removing a module declaration would silently drop an entire suite from the `tests` target. Its existence confirms router and batch behavior are both covered.
