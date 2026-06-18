# sources/object-store/minio-mc/cmd/admin-policy-list.go

## Purpose
Implements `mc admin policy list`/`ls`, listing all canned IAM policies on a MinIO server.

## Important APIs, types, and functions
`adminPolicyListCmd` declares the command. `checkAdminPolicyListSyntax` requires one target. `mainAdminPolicyList` calls `ListCannedPolicies` and prints each policy name via `userPolicyMessage`.

## Control flow
The handler validates the alias, opens an admin client, retrieves the map of policies, then iterates map keys and prints one message per policy.

## State and persistence behavior
This command is read-only. It observes server IAM policy names and does not inspect or write local policy files.

## Dependencies and integration points
It depends on the MinIO admin canned-policy list API, shared policy output message, console colors, global context, and `probe` errors.

## Risks and edge cases
Map iteration order is not deterministic, so human output order may vary. Empty policy maps produce no human lines. The comment incorrectly references policy add, which can mislead maintainers.

## Test signals
Tests should cover syntax validation, empty and populated maps, JSON per-message rendering, non-deterministic order tolerance, and server API errors.
