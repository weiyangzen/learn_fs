# sources/object-store/rustfs/crates/s3select-query/src/test/mod.rs

## Purpose
This test module wires query crate test files into the Rust test harness.

## Important APIs, Types, And Functions
It declares `pub mod error_handling_test;` and `pub mod integration_test;`.

## Control Flow
When crate tests are compiled, both child modules are included.

## State And Persistence Behavior
No local state or persistence.

## Dependencies And Integration Points
This module connects Cargo test discovery with the error-handling and integration test suites.

## Risks And Edge Cases
New test files are ignored unless exported here.

## Test Signals
Its presence ensures both major test suites are compiled and run.
