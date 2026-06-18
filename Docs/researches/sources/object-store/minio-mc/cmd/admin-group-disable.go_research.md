# sources/object-store/minio-mc/cmd/admin-group-disable.go

## Purpose
Defines the hidden mechanics for `mc admin group disable`, which disables an existing MinIO IAM group through the shared enable/disable handler.

## Important APIs, types, and functions
`adminGroupDisableCmd` sets command metadata, usage, flags, help text, and `Action: mainAdminGroupEnableDisable`. There are no additional local helpers.

## Control flow
After the CLI matches `disable`, execution is delegated to `mainAdminGroupEnableDisable` in `admin-group-enable.go`. That shared handler validates two arguments and maps the command name to `madmin.GroupDisabled`.

## State and persistence behavior
The file itself has no state logic. The resulting command mutates persistent server-side group status through `SetGroupStatus`.

## Dependencies and integration points
It depends on the group command registration file, global flags, `setGlobalsFromContext`, and the shared enable/disable implementation.

## Risks and edge cases
Because behavior is selected from `ctx.Command.Name`, renaming this command without updating the shared switch would break status selection. Coverage should include the disable path even though the logic lives elsewhere.

## Test signals
CLI tests should verify command registration, exact two-argument syntax via the shared handler, and that invoking `disable` results in `madmin.GroupDisabled` and a disable-specific message.
