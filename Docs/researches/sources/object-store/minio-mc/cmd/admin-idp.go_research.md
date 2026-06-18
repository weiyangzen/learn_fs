# sources/object-store/minio-mc/cmd/admin-idp.go

## Purpose
Keeps the deprecated `mc admin idp` command as a hidden compatibility entry point that directs users to the newer `mc idp ldap|openid` commands.

## Important APIs, types, and functions
`adminIDPCmd` defines a hidden command with custom deprecation help. `mainAdminIDP` calls `deprecatedError`.

## Control flow
Any invocation of the command bypasses old IDP management behavior and immediately emits the deprecation error pointing to the replacement command family.

## State and persistence behavior
No state is read or changed. The command intentionally prevents legacy configuration mutation through this path.

## Dependencies and integration points
It depends on the CLI command tree, global flags, `setGlobalsFromContext`, and the shared deprecation helper.

## Risks and edge cases
Hidden deprecated commands still occupy names in the admin namespace. If replacement command names change, this message must be updated to avoid stale guidance.

## Test signals
Tests should assert that `mc admin idp` is hidden, returns the deprecation path, and points to `mc idp ldap|openid`.
