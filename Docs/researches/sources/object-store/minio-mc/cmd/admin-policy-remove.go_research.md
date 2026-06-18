# sources/object-store/minio-mc/cmd/admin-policy-remove.go

## Purpose
Implements `mc admin policy remove`/`rm`, deleting a canned IAM policy from a MinIO server.

## Important APIs, types, and functions
`adminPolicyRemoveCmd` declares the command. `checkAdminPolicyRemoveSyntax` requires target and policy name. `mainAdminPolicyRemove` calls `RemoveCannedPolicy` and prints `userPolicyMessage`.

## Control flow
After validation, the handler sets output color, creates an admin client, invokes the server removal API with the policy argument, and prints a success message.

## State and persistence behavior
The persistent mutation is removal of server-side IAM policy definition. Local state is not changed.

## Dependencies and integration points
It integrates MinIO canned-policy removal, global context, shared policy formatting, console colors, and `probe` error tracing.

## Risks and edge cases
The command does not locally check whether the policy is attached to entities; server behavior controls failure or cascading semantics. There is no confirmation prompt.

## Test signals
Tests should cover arity validation, successful API invocation, nonexistent/in-use policy failures, short-name registration, and JSON/human success output.
