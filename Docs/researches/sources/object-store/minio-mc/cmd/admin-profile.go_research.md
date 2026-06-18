# sources/object-store/minio-mc/cmd/admin-profile.go

## Purpose
Defines the deprecated hidden `mc admin profile` command group and redirects users to `mc support profile`.

## Important APIs, types, and functions
`adminProfileSubcommands` includes deprecated start and stop commands. `adminProfileCmd` is hidden. `mainAdminProfile` calls `deprecatedError("mc support profile")`.

## Control flow
Bare group invocation emits group-level deprecation guidance. Start and stop have their own deprecation handlers.

## State and persistence behavior
No profiling state is created, stopped, or downloaded by this group.

## Dependencies and integration points
It integrates with the admin command registry, `minio/cli`, global flags, and deprecation helpers.

## Risks and edge cases
The group remains in the command tree for compatibility while being hidden. New profile functionality should not be added here.

## Test signals
Tests should verify group and subcommands are hidden and all invocations point to the corresponding `mc support profile` replacement.
