# sources/object-store/rustfs/crates/e2e_test/src/protocols/test_runner.rs

## Purpose

This file is the orchestration layer for protocol e2e tests. It builds a feature-filtered test list, runs the selected protocol suites serially, records pass/fail results, logs a summary, and exposes one `#[tokio::test]` entry that fails if any selected suite fails.

## Important APIs, Types, And Functions

`TestResult` records `test_name`, `success`, and optional `error_message`, with constructors `success` and `failure`.

`ProtocolTestSuite` stores `Vec<TestDefinition>`. `new()` reads requested RustFS build features through `requested_rustfs_build_features()` and delegates to `with_requested_features`. The latter filters `all_protocol_tests()` through `rustfs_build_feature_enabled`.

`run_test_suite()` initializes logging, logs the scheduled count, iterates tests in order, emits descriptive start messages, awaits `run_single_test`, records duration and result, sleeps two seconds between tests, then calls `print_summary`.

`run_single_test()` maps stable string names to imported async functions: FTPS core, WebDAV core, SFTP core, SFTP compliance suite, SFTP read-only compliance, SFTP idle timeout, and SFTP standalone compliance. `all_protocol_tests()` defines the stable order and required features.

The `test_protocol_core_suite` `#[tokio::test]` is marked `#[serial]`; it runs the suite and returns an error if any result failed.

## Control Flow

Runtime control is linear and conservative. The feature filter is applied before execution. Each selected test is awaited to completion before the next begins, reducing fixed-port conflicts between protocol suites. Failures are captured into `TestResult` rather than aborting the full loop immediately, so the summary can report every failed selected suite. The final Tokio test converts any failures into one aggregate error.

## State And Persistence Behavior

This file owns no persistent data. It coordinates child-process-owning test bodies in other modules. The only state it maintains is in-memory test definitions, results, and timings. The two-second inter-test delay is a process/port stabilization mechanism rather than persistent state.

## Dependencies And Integration Points

The runner imports public protocol suite functions from FTPS, WebDAV, SFTP core, and SFTP compliance modules. It depends on `common::init_logging`, `requested_rustfs_build_features`, and `rustfs_build_feature_enabled` for logging and feature filtering. `serial_test::serial` ensures the top-level protocol suite does not run concurrently with other serial tests.

## Risks And Edge Cases

The dispatch uses string matching, so names in `all_protocol_tests`, description logging, and `run_single_test` must stay synchronized. Unknown names produce an explicit "not implemented" error. Tests are serial, which reduces interference but makes the full suite expensive, especially when SFTP standalone compliance includes long-running cases. Feature filtering is only as correct as `rustfs_build_feature_enabled`.

## Test Signals

The module has focused unit tests for scheduling behavior: all tests without a filter, non-SFTP feature subsets, SFTP-only scheduling, case-insensitive feature names, `full` scheduling, and no protocol tests for unrelated features. The integration signal is `test_protocol_core_suite`, which fails on any protocol suite failure.
