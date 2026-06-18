# sources/object-store/rustfs/crates/s3select-api/src/test/mod.rs

## Purpose
This test module exposes API-crate query execution tests.

## Important APIs, Types, And Functions
It declares `pub mod query_execution_test;` under test configuration.

## Control Flow
Rust's test harness discovers the child test module when crate tests are compiled.

## State And Persistence Behavior
No runtime state is local to this module.

## Dependencies And Integration Points
It integrates the API crate's tests with Cargo's test module tree.

## Risks And Edge Cases
Only modules listed here are included. Adding new test files requires updating this mod file.

## Test Signals
The presence of `query_execution_test` links the API-level `Output` behavior tests into the suite.
