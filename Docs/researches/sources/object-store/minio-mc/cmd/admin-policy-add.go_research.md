# sources/object-store/minio-mc/cmd/admin-policy-add.go

## Purpose
Preserves the deprecated hidden `mc admin policy add` command and redirects users to `mc admin policy create`.

## Important APIs, types, and functions
`adminPolicyAddCmd` is hidden and uses `mainAdminPolicyAdd`. The handler calls `deprecatedError("mc admin policy create")`.

## Control flow
All invocations immediately emit the deprecation path. No old policy creation API is called.

## State and persistence behavior
No state is read or changed. Policy mutation is intentionally moved to the create command.

## Dependencies and integration points
The file depends on the CLI package, global setup, and shared deprecation helper, and is registered in the policy command group for compatibility.

## Risks and edge cases
Scripts using the old command name will fail with deprecation guidance. The replacement command string must stay synchronized with the active policy command.

## Test signals
Tests should assert the command is hidden, registered, and produces the `mc admin policy create` deprecation message without admin client creation.
