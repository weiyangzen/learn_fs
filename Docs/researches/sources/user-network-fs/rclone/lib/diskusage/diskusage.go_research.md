# sources/user-network-fs/rclone/lib/diskusage/diskusage.go

## Purpose
This file defines the cross-platform disk usage package contract and shared return type.

## Important APIs, types, and functions
- `Info` contains `Free`, `Available`, and `Total` byte counts.
- `ErrUnsupported` is returned by platform implementations that cannot provide disk usage.

## Control flow
There is no runtime flow in this file. Platform-specific files provide `New(dir string)`.

## State and persistence behavior
No state is stored or persisted.

## Dependencies and integration points
The only dependency is `errors`. All platform-specific `diskusage_*` files share this type and error value so callers can handle unsupported platforms consistently.

## Risks and edge cases
The semantic difference between `Free` and `Available` depends on platform syscalls and filesystem privilege rules. Callers must not assume every platform supports the probe.

## Test signals
`diskusage_test.go` consumes `Info` and `ErrUnsupported` through the platform `New` implementation.
