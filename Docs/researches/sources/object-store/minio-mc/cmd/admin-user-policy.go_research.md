# sources/object-store/minio-mc/cmd/admin-user-policy.go

## Purpose

`admin-user-policy.go` implements `mc admin user policy`, exporting the effective policy document attached directly to a user.

## Important APIs, Types, and Functions

`adminUserPolicyCmd` defines the command. `mainAdminUserPolicy` calls `GetUserInfo`, fetches each named policy with `getPolicyInfo`, unmarshals to `policy.Policy`, merges policies with `policy.MergePolicies`, and writes JSON to stdout.

## Control Flow

The handler validates target and username, fetches user info, fails when no policy name is set, splits comma-separated policy names, fetches each policy document, parses it, merges all non-empty names, and encodes the merged policy directly to `os.Stdout`.

## State and Persistence Behavior

The command reads remote IAM policies and writes only stdout. It does not use the normal `printMsg` JSON wrapper for the final policy document.

## Dependencies and Integration Points

It depends on admin client policy helpers from elsewhere in the package, `github.com/minio/pkg/v3/policy`, color JSON decoding, and standard output.

## Risks and Edge Cases

Group-derived policies are not included here unless present in `user.PolicyName`. Comma splitting does not trim whitespace. Direct stdout encoding bypasses the usual status envelope and color handling.

## Test Signals

Tests should cover missing policy, multiple policy merge semantics, malformed policy JSON, empty names in comma-separated strings, and exact stdout JSON.
