# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/mod.rs

## Purpose
This is the failpoint test crate root for raftstore-v2. It enables nightly custom test framework support, selects `test_util::run_failpoint_tests` as the test runner, imports the shared integration `cluster` harness, and declares the failpoint test modules.

## Important APIs, Types, and Functions
There are no runtime APIs. The important declarations are `#![feature(test)]`, `#![feature(custom_test_frameworks)]`, `#![test_runner(test_util::run_failpoint_tests)]`, the path import of `../integrations/cluster.rs`, and module declarations for failpoint suites.

## Control Flow
Cargo compiles this test target with failpoints enabled. The custom runner executes the module tests under TiKV's failpoint-test harness, so failpoint state setup and teardown semantics are controlled by `test_util`.

## State and Persistence Behavior
This file has no direct state or persistence behavior. It shapes test execution and ensures failpoint tests share the same cluster helper as normal integrations.

## Dependencies and Integration Points
It integrates failpoint tests with the `cluster` module used by normal integration tests. This matters because failpoint cases exercise the same real raftstore-v2 system startup, tablet registry, PD client, and transport behavior as non-failpoint tests.

## Risks and Edge Cases
- Sharing `cluster.rs` through a path import means helper changes affect both integration and failpoint targets.
- The custom test runner is required; running these modules under a plain harness could leave failpoints unmanaged.

## Test Signals
The module list shows the intended failpoint coverage areas: basic write/apply, bootstrap, bucket refresh, peer life, merge, PD heartbeat, split, and trace apply.
