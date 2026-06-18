# sources/user-network-fs/nfs-ganesha/src/include/os/quota.h

## Purpose
This wrapper selects the platform quota abstraction for Ganesha quota and rquota code.

## Important APIs, Types, And Control Flow
It conditionally includes `<os/linux/quota.h>` for Linux or `<os/freebsd/quota.h>` for FreeBSD. It exports the platform-selected `QUOTACTL` interface through that include.

## State And Persistence
The wrapper has no state. Underlying quota operations read or mutate filesystem quota state.

## Dependencies And Integration Points
It is a stable include point for rquota service handlers and FSAL quota paths.

## Risks And Test Signals
Risk comes from platform macro selection and differing quota command interfaces. Test signals include Linux and FreeBSD builds, rquota RPC behavior, disabled quota behavior, and permission-denied paths.
