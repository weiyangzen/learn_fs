# sources/storage-engines/tikv/components/cdc/tests/integrations/mod.rs

## Purpose
This module is the integration test harness root for non-failpoint CDC integration tests. It declares the integration suites and re-exports common test-suite helpers.

## Important APIs, Types, and Functions
- Modules: `test_cdc` and `test_flow_control`.
- `#[path = "../mod.rs"] mod testsuite; pub use testsuite::*;` shares cluster/event-feed helper APIs with the integration tests.

## Control Flow
Rust test discovery loads the declared integration modules through this root. Individual test functions live in the child modules; this file only establishes module topology.

## State and Persistence Behavior
No runtime or persistent state is managed here. It affects compilation and test organization only.

## Dependencies and Integration Points
The file links integration tests with the shared CDC test suite infrastructure used by failpoint tests, allowing common cluster builders, clients, and event-feed utilities.

## Risks and Edge Cases
The main risk is organizational: missing module declarations would silently omit integration coverage from this harness. Shared helper re-export means changes in parent `tests/mod.rs` propagate to both failpoint and integration suites.

## Test Signals
The signal from this file is successful compilation and discovery of `test_cdc` and `test_flow_control`; behavioral assertions are in those modules.
