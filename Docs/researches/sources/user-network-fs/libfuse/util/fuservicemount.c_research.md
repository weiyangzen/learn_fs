# sources/user-network-fs/libfuse/util/fuservicemount.c

## Purpose
Small wrapper executable for service-based FUSE mounting. It either checks for an available service socket for a filesystem type or delegates to `mount_service_main`.

## Important APIs, Types, And Functions
- `check_service` returns success only if `mount_service_present(fstype)` is true.
- `main` recognizes the exact `-t FSTYPE --check` shape, rejects ambiguous duplicates, and otherwise calls `mount_service_main`.

## Control Flow
The argument scanner accepts only `--check` and one `-t` pair for check mode. Any other argument shape disables check mode and runs the full mount service client.

## State And Persistence
No persistent state. Any mount effects are delegated to `mount_service_main`.

## Dependencies And Integration Points
Built when service mount support is configured. Invoked by `mount.fuse.c` via install path or `PATH`, and may be run by administrators or tooling to test service availability.

## Risks
`--check` only verifies socket presence/access, not that a healthy service will complete a mount. Argument acceptance is intentionally narrow; wrapper behavior can differ from full mount mode for unusual argument orders.

## Test Signals
Test `--check` with missing type, duplicate type/check flags, inaccessible socket, non-socket path, and normal fallback to `mount_service_main`.
