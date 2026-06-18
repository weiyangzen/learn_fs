# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_log.c

## Purpose

`ufs_log.c` is a small ioctl wrapper layer for enabling, disabling, and querying UFS logging. It delegates the real logging implementation to the logging subsystem while handling user/kernel copy semantics and status reporting.

## Main Interfaces

- `ufs_fiologenable()` copies in a `fiolog_t`, calls `lufs_enable()`, copies the possibly updated structure back out, and returns the logging operation status unless copyout fails.
- `ufs_fiologdisable()` copies in a `fiolog_t`, calls `lufs_disable()`, copies the result back out, and returns the operation status unless copyout fails.
- `ufs_fioislog()` reports whether the mount has an active `vfs_log`.

## Behavior

The enable and disable paths use `ddi_copyin()` and `ddi_copyout()` with ioctl flags, so they support kernel/user ioctl contexts consistently. They return `EFAULT` on copy failure and otherwise preserve the result from the lower logging function.

`ufs_fioislog()` reads `VTOI(vp)->i_ufsvfs` and checks `vfs_log`. For kernel ioctls (`FKIOCTL`) it writes directly to `*islog`; for user callers it uses `suword32()` and returns `EFAULT` if the user write fails.

## Invariants And Dependencies

Key invariants:

- Logging state is represented at the mount level by `ufsvfs_t.vfs_log`.
- Enable/disable request structures are round-tripped to the caller because lower layers may update fields.
- User-space status writes must use safe copyout helpers.

Dependencies include `lufs_enable()`, `lufs_disable()`, UFS inode-to-mount conversion, ioctl flag conventions, and low-level safe copy helpers.

## Research Notes

This file intentionally contains almost no policy. Permission checks, log allocation, lockfs interaction, and mount-state changes live below `lufs_enable()` and `lufs_disable()`. The main thing to verify around this wrapper is copyin/copyout ordering: a successful logging operation can still be reported as `EFAULT` if the updated structure cannot be copied back.
