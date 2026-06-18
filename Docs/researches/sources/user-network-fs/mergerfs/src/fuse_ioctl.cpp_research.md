# sources/user-network-fs/mergerfs/src/fuse_ioctl.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_ioctl.cpp` implements ioctl pass-through for open files and directories with safety filters. The source was read as a complete 207-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::ioctl`, `FS_IOC_*`, `fs::ioctl`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::ioctl` rejects btrfs ioctls, works around `FS_IOC_*` size issues, opens directory targets by policy, and delegates to `fs::ioctl`.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_ioctl.hpp", "fuse_getxattr.hpp", "fuse_setxattr.hpp", "config.hpp", "dirinfo.hpp", "endian.hpp", "errno.hpp", "fileinfo.hpp". Big-endian systems reject problematic flag/version ioctls. Directory ioctl depends on `FUSE_IOCTL_DIR` and open policy.

## Risks and Edge Cases

Big-endian systems reject problematic flag/version ioctls. Directory ioctl depends on `FUSE_IOCTL_DIR` and open policy.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
