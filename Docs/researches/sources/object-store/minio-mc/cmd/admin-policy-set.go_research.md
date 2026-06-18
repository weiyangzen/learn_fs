# sources/object-store/minio-mc/cmd/admin-policy-set.go

## Purpose
Keeps the deprecated hidden `mc admin policy set` command and redirects users to `mc admin policy attach`.

## Important APIs, types, and functions
`adminPolicySetCmd` defines the hidden command and `mainAdminPolicySet` calls `deprecatedError("mc admin policy attach")`.

## Control flow
No legacy policy mapping behavior remains. Invocation immediately emits deprecation guidance.

## State and persistence behavior
No server or local state is changed. Policy association mutation is handled by the attach command.

## Dependencies and integration points
It depends on the CLI command registry and shared deprecation helper, and is included in `adminPolicySubcommands` for compatibility.

## Risks and edge cases
Legacy scripts must migrate. The command name is still reserved, so future reuse would require compatibility care.

## Test signals
Tests should verify hidden registration and deprecation output pointing to `mc admin policy attach`.
