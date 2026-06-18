# sources/object-store/rustfs/crates/policy/tests/policy_is_allowed.rs

## Purpose

Integration-style test matrix for `Policy::is_allowed`. It builds policies and request arguments directly and checks allow/deny outcomes across action matching, resource matching, conditions, deny statements, and NotResource behavior.

## Important APIs, Types, and Functions

- `ArgsBuilder` is a convenience struct with owned fields for account, groups, action string, bucket, conditions, owner flag, object, claims, and deny-only flag.
- `policy_is_allowed(policy, args) -> bool` converts `ArgsBuilder` into runtime `Args`, parses action strings, and blocks on async policy evaluation with `pollster`.
- The `#[test_case]` matrix supplies many concrete policies and expected booleans.

## Control Flow

Each test case constructs a `Policy` with one statement, creates request args, then calls `Policy::is_allowed`. Empty `groups` becomes `None`; non-empty groups are cloned into `Some(Vec<String>)`. Action strings are parsed through `try_into`, so invalid action strings would panic in test setup.

## State and Persistence

No state or persistence. Tests allocate temporary policy/request values only.

## Dependencies and Integration Points

Imports the public `rustfs_policy::policy` API, S3 actions, serde JSON values, `HashMap`, and `test_case`. It exercises the crate as an external consumer rather than through private module access.

## Risks and Edge Cases

- Cases are numbered and somewhat repetitive, so failures can require inspecting the embedded policy/request pair.
- Tests mostly use single-statement policies; complex multi-statement interactions are covered more in `policy.rs`.
- Because `pollster::block_on` is used, the test avoids tokio runtime assumptions for policy evaluation.

## Test Signals

The matrix verifies:

- Allowed S3 actions against wildcard resources.
- Denial when action does not match.
- Object resource pattern matching.
- IP address condition success and failure using `aws:SourceIp`/`SourceIp`.
- Deny effect precedence for matching deny statements.
- `NotResource` allow outside a blacklist and denial inside the blacklist.

These tests complement inline unit tests by confirming the public policy evaluation API behavior.
