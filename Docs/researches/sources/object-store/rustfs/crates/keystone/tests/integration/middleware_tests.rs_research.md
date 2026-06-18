# sources/object-store/rustfs/crates/keystone/tests/integration/middleware_tests.rs

## Purpose
This integration test module verifies Keystone middleware construction and Tokio task-local credential behavior from outside the crate, using the public `rustfs_keystone` API.

## Important APIs, Types, and Functions
Helpers `create_test_auth_provider` and `create_test_credentials` construct a disabled-real-network provider and test `Credentials`. Tests cover `KeystoneAuthLayer::new`, `KEYSTONE_CREDENTIALS.scope`, task isolation across spawned Tokio tasks, `None` scopes, claims preservation, nested scopes, auth provider construction with cache enabled/disabled, sequential scopes, and outside-scope access.

## Control Flow
Most async tests enter a task-local scope with `Some(Credentials)` or `None`, read `KEYSTONE_CREDENTIALS` using `try_with`, and assert values or absence. The isolation test spawns two concurrent tasks with different scoped credentials and confirms each task sees its own parent user. The nested-scope test confirms inner scope overrides outer scope while active.

## State and Persistence Behavior
The tests create only in-memory credentials and providers. They do not start a Keystone server or persist anything. `create_test_auth_provider` disables SSL verification against localhost but never sends requests.

## Dependencies and Integration Points
The file imports `rustfs_credentials::Credentials`, public middleware task-local storage, and public `KeystoneAuthLayer`, `KeystoneAuthProvider`, `KeystoneClient`, and `KeystoneVersion`. It validates that external crates can use the public API surface.

## Risks and Edge Cases
These tests do not exercise actual Tower service invocation, HTTP body boxing, 401 responses, XML escaping, header parsing, or Keystone network validation. Test credentials use a claim shape under `"keystone"` that differs from production `auth.rs`, which inserts flat keys such as `"keystone_user_id"` and `"keystone_roles"`.

## Test Signals
The suite gives strong signal for task-local scoping semantics and public constructor compatibility. It gives weak signal for end-to-end middleware authentication correctness.
