# sources/object-store/rustfs/crates/keystone/tests/integration/mod.rs

## Purpose
`mod.rs` is the integration-test entrypoint declared by `Cargo.toml`. It currently includes the `middleware_tests` module.

## Important APIs, Types, and Functions
The file has one module declaration: `mod middleware_tests;`. It contains no direct tests or helper functions.

## Control Flow and Integration Points
Cargo runs this file as the `integration` test target. The module declaration pulls in `middleware_tests.rs`, allowing that file's tests to run as an external crate integration suite.

## State and Persistence Behavior
No runtime state or persistence.

## Dependencies
Dependencies are inherited from the integration test target and the child module.

## Risks and Edge Cases
Only middleware integration tests are wired. Other Keystone integration areas, such as client parsing against a mock Keystone API or identity mapper behavior from an external crate, are not represented here.

## Test Signals
The existence of this file confirms the integration suite is intentionally scoped to middleware tests at present.
