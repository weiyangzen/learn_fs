# sources/object-store/minio-mc/cmd/admin-group-enable.go

## Purpose
Implements the shared handler for `mc admin group enable` and `mc admin group disable`, changing a group's active status in MinIO IAM.

## Important APIs, types, and functions
`adminGroupEnableCmd` defines the enable command. `checkAdminGroupEnableSyntax` requires target and group name. `mainAdminGroupEnableDisable` maps command names to `madmin.GroupEnabled` or `madmin.GroupDisabled` and calls `SetGroupStatus`.

## Control flow
The handler validates syntax, initializes output color, opens an admin client, reads the group name, chooses the target status from `ctx.Command.Name`, invokes the server API, then prints a `groupMessage` whose operation is either `enable` or `disable`.

## State and persistence behavior
The only persistent effect is remote group status stored by MinIO. The local message includes `GroupStatus`, but human rendering uses the operation name rather than the status field.

## Dependencies and integration points
It integrates `madmin-go` group status constants, shared client creation, global context, `fatalIf`, `probe`, and the `groupMessage` type from the add file.

## Risks and edge cases
The default switch case handles unexpected command names, which protects against accidental reuse. There is no local existence check; server errors are surfaced. Disable command behavior depends on this file even though the disable command is declared separately.

## Test signals
Good tests mock both enable and disable command names, assert `SetGroupStatus` receives the correct enum, verify invalid command name handling, and check human/JSON output through `printMsg`.
