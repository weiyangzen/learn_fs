# sources/object-store/minio-mc/cmd/admin-policy-update.go

## Purpose
Keeps the deprecated hidden `mc admin policy update` command and redirects users to `mc admin policy attach`.

## Important APIs, types, and functions
`adminPolicyUpdateCmd` declares the hidden command. `mainAdminPolicyUpdateErr` calls `deprecatedError("mc admin policy attach")`.

## Control flow
All invocations terminate through deprecation handling; no policy update API is called.

## State and persistence behavior
No local or remote state is modified.

## Dependencies and integration points
It integrates with policy command registration and shared deprecation messaging.

## Risks and edge cases
The command's legacy wording says attach a new policy, but modern behavior is a hard redirect. Stale scripts need migration.

## Test signals
Tests should verify hidden registration and that invocation produces the attach deprecation guidance.
