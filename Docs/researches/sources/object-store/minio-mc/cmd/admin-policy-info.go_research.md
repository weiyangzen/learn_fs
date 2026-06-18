# sources/object-store/minio-mc/cmd/admin-policy-info.go

## Purpose
Implements `mc admin policy info`, retrieving a canned IAM policy and optionally writing its JSON document to a local file.

## Important APIs, types, and functions
Important symbols are `policyInfoFlags`, `adminPolicyInfoCmd`, `checkAdminPolicyInfoSyntax`, `getPolicyInfo`, and `mainAdminPolicyInfo`. `getPolicyInfo` first calls `InfoCannedPolicyV2` and falls back to deprecated `InfoCannedPolicy` when needed.

## Control flow
The handler validates target and policy name, creates an admin client, fetches policy metadata through the compatibility helper, optionally creates and writes a `--policy-file`, then prints `userPolicyMessage` with the full `madmin.PolicyInfo`.

## State and persistence behavior
Server IAM policy state is read. If `--policy-file` is set, local filesystem state is overwritten/created with the policy bytes.

## Dependencies and integration points
It integrates new and old MinIO canned-policy APIs, local file output, global context, console colors, and shared policy serialization.

## Risks and edge cases
`os.Create` truncates existing policy files. The fallback path is necessary for older servers and should not be removed without compatibility review. File close errors are not explicitly checked.

## Test signals
Tests should cover V2 success, old-server fallback, nonexistent policy errors, policy-file creation/write failures, JSON policy info output, and exact two-argument syntax.
