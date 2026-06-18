# sources/storage-engines/tikv/components/cdc/tests/failpoints/mod.rs

## Purpose
This module is the failpoint test harness root for CDC. It enables the custom failpoint test runner, declares the individual failpoint test modules, and re-exports the common CDC test suite helpers.

## Important APIs, Types, and Functions
- `#![feature(custom_test_frameworks)]` and `#![test_runner(test_util::run_failpoint_tests)]` configure failpoint-aware test execution.
- Modules: `test_endpoint`, `test_memory_quota`, `test_observe`, `test_register`, and `test_resolve`.
- `#[path = "../mod.rs"] mod testsuite; pub use testsuite::*;` exposes shared cluster/client helpers.

## Control Flow
The Rust test framework discovers tests in the declared modules and runs them through `run_failpoint_tests`, ensuring failpoint setup/cleanup behavior is suitable for injected failure cases.

## State and Persistence Behavior
This file stores no runtime state. It determines compilation/test topology only.

## Dependencies and Integration Points
It ties the CDC failpoint suites to the broader test utility framework and the integration test suite definitions in the parent `tests` module.

## Risks and Edge Cases
Because all failpoint modules share one harness root, leaked failpoints in one test can affect later tests. Individual tests mostly remove failpoints explicitly, but ignored/panic paths remain a standard failpoint-suite risk.

## Test Signals
The file itself has no tests; its signal is successful compilation/discovery and execution of the five declared failpoint suites.
