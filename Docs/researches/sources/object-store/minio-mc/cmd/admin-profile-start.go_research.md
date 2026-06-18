# sources/object-store/minio-mc/cmd/admin-profile-start.go

## Purpose
Maintains the deprecated hidden `mc admin profile start` command and redirects to `mc support profile start`.

## Important APIs, types, and functions
`adminProfileStartCmd` defines command metadata. `mainAdminProfileStart` calls `deprecatedError("mc support profile start")`.

## Control flow
The command performs no profiling action. Invocation immediately reports the replacement command.

## State and persistence behavior
No profiling state is started locally or remotely through this path.

## Dependencies and integration points
It depends on CLI registration, global setup, and the deprecation helper. It is a subcommand of the hidden admin profile group.

## Risks and edge cases
Legacy automation will no longer start profiles through `mc admin`. Replacement guidance must track the support command.

## Test signals
Tests should verify hidden command metadata and deprecation output pointing to `mc support profile start`.
