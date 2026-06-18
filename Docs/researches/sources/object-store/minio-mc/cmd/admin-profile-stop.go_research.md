# sources/object-store/minio-mc/cmd/admin-profile-stop.go

## Purpose
Maintains the deprecated hidden `mc admin profile stop` command and redirects to `mc support profile stop`.

## Important APIs, types, and functions
`adminProfileStopCmd` defines command metadata with global flags. `mainAdminProfileStop` calls `deprecatedError("mc support profile stop")`.

## Control flow
The command does not stop or download profile data. It immediately emits replacement-command guidance.

## State and persistence behavior
No profile collection state or local profile files are touched.

## Dependencies and integration points
It depends on CLI registration, global flags, and shared deprecation plumbing.

## Risks and edge cases
Keeping global flags on a deprecated command may imply old behavior still exists. Scripts must migrate to support commands.

## Test signals
Tests should assert hidden registration and the exact replacement target in the deprecation message.
