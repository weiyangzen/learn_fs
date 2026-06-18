# sources/object-store/minio-mc/cmd/admin-policy-attach.go

## Purpose
Implements `mc admin policy attach` and the shared attach/detach helper for associating IAM policies with a user or group.

## Important APIs, types, and functions
`adminAttachPolicyFlags` defines `--user` and `--group`. `adminPolicyAttachCmd` uses `mainAdminPolicyAttach`, which calls `userAttachOrDetachPolicy(ctx, true)`. The helper builds `madmin.PolicyAssociationReq` and calls either `AttachPolicy` or `DetachPolicy`.

## Control flow
The helper requires target plus at least one policy. It reads user/group flags, treats all remaining args as policies, creates an admin client, calls the chosen association API, tolerates `XMinioAdminPolicyChangeAlreadyApplied`, backfills a response for older servers that returned no timestamp, and prints `policyAssociationMessage`.

## State and persistence behavior
The persistent effect is changing MinIO IAM policy associations for a user or group. Local state is limited to the request and compatibility response construction.

## Dependencies and integration points
It integrates `madmin-go` IAM association APIs, server error-code translation, global context, shared policy output types, and the detach command's implementation.

## Risks and edge cases
The help says exactly one of user or group is required, but this helper does not locally enforce exclusivity; it relies on server behavior. Compatibility backfill may hide old-server response differences. Already-applied changes are treated as success.

## Test signals
Tests should cover attach and detach modes, multiple policy args, user/group flag combinations, already-applied errors, old-server empty responses, and fatal behavior for real API failures.
