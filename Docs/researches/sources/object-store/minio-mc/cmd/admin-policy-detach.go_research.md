# sources/object-store/minio-mc/cmd/admin-policy-detach.go

## Purpose
Defines `mc admin policy detach`, detaching one or more policies from a user or group through the shared policy association helper.

## Important APIs, types, and functions
`adminDetachPolicyFlags` mirrors attach flags for `--user` and `--group`. `adminPolicyDetachCmd` points to `mainAdminPolicyDetach`, which calls `userAttachOrDetachPolicy(ctx, false)`.

## Control flow
The file delegates all validation and server interaction to the helper in `admin-policy-attach.go`. The helper selects `DetachPolicy`, handles already-applied responses, and prints an association message.

## State and persistence behavior
The resulting command mutates server-side IAM policy associations by removing mappings from the selected user or group.

## Dependencies and integration points
It depends on the attach helper, global flags, CLI command registration, and shared policy output types.

## Risks and edge cases
Attach and detach share validation gaps around user/group exclusivity. Any helper change affects both commands. The short local file can be missed by tests if only attach is covered.

## Test signals
Tests should verify detach command registration, flag names, dispatch with `attach=false`, multiple policy support, and old-server response backfill for detached policies.
