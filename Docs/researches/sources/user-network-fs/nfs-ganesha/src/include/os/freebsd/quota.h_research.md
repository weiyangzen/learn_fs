# sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/quota.h

## Purpose
This FreeBSD quota shim normalizes quota syscall naming and quota-block structure field names for Ganesha code shared with Linux.

## Important APIs, Types, And Functions
It includes `<ufs/ufs/quota.h>`. `QUOTACTL(cmd, path, id, addr)` maps generic call sites to FreeBSD `quotactl(path, cmd, id, (void *)addr)`. `struct dqblk_os` mirrors the quota fields expected by Ganesha, using `dqb_curspace` rather than FreeBSD's differently named member. On newer FreeBSD compiler versions it undefines `dqblk`, then maps `dqblk` to `dqblk_os`.

## Control Flow
Shared quota code calls `QUOTACTL` and refers to `struct dqblk` fields. This header rewrites those compile-time names so FreeBSD builds call the native syscall with the correct argument order and use the compatibility quota structure.

## State And Persistence
The header has no state. Runtime quota state is read or written through `quotactl` depending on the command. `dqblk_os` instances are caller-owned buffers representing quota limits, usage, and grace times.

## Dependencies And Integration Points
It integrates FSAL quota/reporting code with FreeBSD UFS quota definitions. It also depends on FreeBSD-specific `__FreeBSD_cc_version` behavior for the `dqblk` macro adjustment.

## Risks And Test Signals
Risks include structure layout mismatch with kernel expectations, command argument-order mistakes, macro replacement leaking into unrelated includes, and version-guard drift. Test signals include FreeBSD quota compile tests, `QUOTACTL` get/set smoke tests against a quota-enabled filesystem, field-value round trips for block/inode usage, and builds across supported FreeBSD versions.
