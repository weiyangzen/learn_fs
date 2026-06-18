# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_suspend.c

## Role

Implements the `/dev/ufssuspend` character device used to suspend and resume writes to an FFS filesystem, and to permit controlled raw block reads/writes while the filesystem is suspended.

## Main Responsibilities

- Registers the `ffs_susp` character device.
- Implements `UFSSUSPEND` and `UFSRESUME` ioctls.
- Uses VFS write suspension to quiesce a mounted FFS filesystem.
- Associates a suspended mount with the caller’s file descriptor through `devfs_set_cdevpriv()`.
- Automatically resumes the filesystem when the descriptor is closed.
- Allows block-aligned reads and writes to the underlying device while suspended.
- Reloads filesystem metadata before unsuspending after forced descriptor cleanup.

## Character Device Interface

`ffs_susp_cdevsw` provides:

- `ffs_susp_open()`: trivial open.
- `ffs_susp_rdwr()`: read/write handler for raw device blocks.
- `ffs_susp_ioctl()`: suspend/resume control path.

`ffs_susp_initialize()` creates `/dev/ufssuspend` with mode `0600`; `ffs_susp_uninitialize()` destroys it.

## Suspend Flow

`ffs_susp_ioctl(UFSSUSPEND)`:

1. Rejects jailed callers.
2. Looks up the mount by `fsid_t`.
3. Takes a busy reference.
4. Requires the calling process to be single-threaded.
5. Checks that the process has no writable descriptors on the target mount.
6. Calls `ffs_susp_suspend()`.
7. Stores the mount in cdev private data with `ffs_susp_dtor()` as destructor.

`ffs_susp_suspend()`:

- Verifies the mount belongs to FFS via `ffs_own_mount()`.
- Rejects already suspended mounts.
- Checks read/write access to the original device vnode.
- Runs MAC mount stat policy when enabled.
- Calls `vfs_write_suspend(mp, VS_SKIP_UNMOUNT)`.
- Sets `UM_WRITESUSPENDED`.

## Resume Flow

`ffs_susp_ioctl(UFSRESUME)` clears the cdev private data. That invokes `ffs_susp_dtor()`, which:

- Checks whether the mount is still suspended.
- Calls `ffs_reload(mp, FFSR_FORCE | FFSR_UNSUSPEND)` to reload metadata and clear suspension flags.
- Panics if reload fails, since leaving the filesystem suspended would be fatal.
- Calls `ffs_susp_unsuspend()`.

`ffs_susp_unsuspend()` works around the fact that `vfs_write_resume()` expects the resuming thread to match the suspending thread by assigning `mp->mnt_susp_owner = curthread`, then resumes writes, clears `UM_WRITESUSPENDED`, and unbusies the mount.

## Raw I/O While Suspended

`ffs_susp_rdwr()`:

- Requires cdev private data to identify a suspended mount.
- Rejects I/O if the mount is not currently suspended.
- Operates on `ump->um_devvp`.
- Requires user-space `uio`.
- Requires offsets and lengths aligned to filesystem fragment boundaries.
- Limits each transfer to `fs->fs_bsize`.
- Uses `bread()` to read the device block.
- For writes, copies user data into the buffer and calls `bwrite()`.
- For reads, copies buffer contents back to userland and releases the buffer.

This interface supports tools that need a stable on-disk image while normal filesystem mutation is blocked.

## Locking and State

- `ffs_susp_lock` serializes suspend/resume and raw I/O state.
- Shared locking protects read/write access while suspended.
- Exclusive locking protects suspend/resume transitions.
- `UM_WRITESUSPENDED` records FFS-level suspended state.
- `MNTK_SUSPEND` is asserted during destructor cleanup.

## Research Relevance

This file is relevant for snapshotting, fsck, backup, and external metadata tooling research. It shows how FreeBSD exposes a privileged, descriptor-scoped write suspension mechanism and how that mechanism coordinates VFS suspension, FFS reload, raw device access, and process lifetime cleanup.
