# sources/object-store/minio-mc/cmd/admin-policy-unset.go

## Purpose
Keeps the deprecated hidden `mc admin policy unset` command and redirects users to `mc admin policy detach`.

## Important APIs, types, and functions
`adminPolicyUnsetCmd` defines command metadata. `mainAdminPolicyUnsetErr` invokes `deprecatedError("mc admin policy detach")`.

## Control flow
The command always follows the deprecation path and performs no policy detachment itself.

## State and persistence behavior
No state is read or written. Active policy detachment is implemented by `admin-policy-detach.go`.

## Dependencies and integration points
It depends on CLI registration, global setup, and the shared deprecation mechanism.

## Risks and edge cases
Deprecated hidden commands can still be invoked by automation. Replacement guidance must remain accurate.

## Test signals
Tests should assert hidden command metadata and deprecation output for `mc admin policy detach`.
