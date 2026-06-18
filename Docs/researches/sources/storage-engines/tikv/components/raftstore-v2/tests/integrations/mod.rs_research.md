# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/mod.rs

## Purpose
This is the normal raftstore-v2 integration test crate root. It enables nightly custom test framework support, selects `test_util::run_tests`, and declares the integration modules.

## Important APIs, Types, and Functions
There are no runtime APIs. The file declares modules for the shared `cluster` harness and the test suites covering basic writes, conf changes, life cycle, merge, PD heartbeat, read, split, status, trace apply, and transfer leader.

## Control Flow
Cargo compiles this target and the custom test runner executes all declared module tests. The comment notes conflict-control tests are deferred until split support is ready.

## State and Persistence Behavior
This file has no direct persistence behavior. It controls which integration tests are compiled and run together.

## Dependencies and Integration Points
It integrates with `test_util::run_tests` and the module tree under `tests/integrations`.

## Risks and Edge Cases
- Excluding a module here silently removes its integration coverage.
- The custom test runner is required for TiKV test setup conventions.

## Test Signals
The module list is the high-level integration coverage map for raftstore-v2 in this subset.
