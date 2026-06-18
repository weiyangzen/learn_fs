# File Research: sources/os/linux/linux/fs/coda/pioctl.c

## Purpose
Implements Coda pioctl support, allowing userspace control operations to be routed through a special ioctl file into Venus for a target Coda path.

## Main Elements
- `coda_ioctl_inode_operations`: denies execute permission and delegates setattr to `coda_setattr()`.
- `coda_ioctl_operations`: exposes `coda_pioctl()` through `.unlocked_ioctl`.
- `coda_pioctl()`: copies `PioctlData` from userspace, resolves the supplied path with optional symlink following, verifies the target inode belongs to the same Coda superblock, then calls `venus_pioctl()` with the target fid.
- `coda_ioctl_permission()`: allows non-exec accesses and rejects `MAY_EXEC`.

## Dependencies And Integration
Bridges VFS ioctl entry points to `venus_pioctl()` in `upcall.c`. Uses normal pathname resolution via `user_path_at()` and Coda inode conversion through `ITOC()`.

## Risk Notes
The path argument comes from userspace and must resolve to the same mounted Coda instance; otherwise the ioctl is rejected. The actual command and payload validation is split between this wrapper and `venus_pioctl()`, where payload size and copy-in/copy-out checks are enforced.
