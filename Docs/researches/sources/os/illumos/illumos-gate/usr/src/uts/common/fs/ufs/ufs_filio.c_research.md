# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_filio.c

## Purpose

`ufs_filio.c` implements UFS filesystem-specific ioctl helpers. These operations expose private or semi-private controls for inode-open-by-number, access-time setting, delayed I/O, filesystem flushing, busy checks, direct-I/O toggling, tunables, hole/data seeking, and compressed-file marking.

Many routines are explicitly described as tailored to historical consumers such as Metamucil or contract-private backup products, so they are part of the compatibility/control surface rather than normal VFS behavior.

## Main Interfaces

- `ufs_fioio()` opens a file by inode number and generation.
- `ufs_fiosatime()` sets access time without changing change time.
- `ufs_fiogdio()` and `ufs_fiosdio()` get/set delayed-I/O state.
- `ufs_fioffs()` flushes a whole filesystem.
- `ufs_fioisbusy()` reports whether a vnode has external references or mappings.
- `ufs_fiodirectio()` toggles per-inode direct-I/O mode.
- `ufs_fiotune()` updates mounted filesystem tunables.
- `ufs_fio_holey()` implements seek-hole/seek-data support.
- `ufs_mark_compressed()` marks a regular file as compressed.

## Ioctl Behaviors

`ufs_fioio()` is privileged. It copies in a `fioio` structure, validates the inode number against filesystem bounds, obtains the inode with `ufs_iget()`, checks generation and allocation state, allocates a file descriptor with large-file semantics, checks read access, opens the vnode, and returns the descriptor to userland. On error it releases the allocated file structure and vnode hold.

`ufs_fiosatime()` is privileged and either sets atime to the current unique UFS time or to a copied-in timeval, with ILP32/LP64 conversion and overflow validation. It marks `IMODACC` so the access-time change is persisted without treating ctime as changed.

`ufs_fiogdio()` returns mount delayed-I/O state. `ufs_fiosdio()` changes it only for non-logging filesystems, quiescing the filesystem, flushing data, updating `vfs_dio`, and setting `fs_clean` to `FSSUSPEND` or `FSACTIVE` for writable non-bad/non-log filesystems.

`ufs_fioffs()` flushes the filesystem from ioctl or VFS entry points. It suspends the delete thread, quiesces lockfs, may make a non-rollable log rollable and restart reclaim, flushes all dirty data/metadata with `ufs_flush()`, then resumes delete processing.

## Utility Controls

`ufs_fioisbusy()` purges DNLC references when `v_count > 1`, then reports busy if the vnode has more than the caller's reference or if `i_mapcnt` is nonzero.

`ufs_fiodirectio()` sets or clears `IDIRECTIO` under `i_contents` and `i_tlock` for `DIRECTIO_ON` or `DIRECTIO_OFF`.

`ufs_fiotune()` validates and applies mounted filesystem tunables (`maxcontig`, `rotdelay`, `maxbpg`, `minfree`, `optim`), recomputes `vfs_ioclustsz` and `vfs_minfrags`, and writes the superblock through UFS transaction macros if the filesystem is writable.

`ufs_fio_holey()` implements `_FIO_SEEK_HOLE` and `_FIO_SEEK_DATA`. It returns `ENXIO` when the starting offset is at or beyond EOF, fast-paths no-hole files by returning EOF as the virtual hole, and otherwise uses `bmap_find()` to locate the next hole or data extent.

`ufs_mark_compressed()` validates regular-file type, sets `ICOMPRESS`, logs the inode, marks ctime/sequence changes, and updates the inode asynchronously when logging is not active.

## Invariants And Dependencies

Key invariants:

- Configuration-changing ioctls require `secpolicy_fs_config()`.
- Delayed-I/O changes are blocked under logging and require quiesce plus flush.
- Filesystem flush must coordinate with lockfs, delete thread, log rolling, reclaim state, and superblock updates.
- Hole/data seeking relies on UFS block mapping rather than byte-by-byte scanning.

Dependencies include lockfs (`ufs_quiesce`, `ufs_flush`), inode cache lookup, DNLC purge, UFS transaction macros, logmap rolling, quota/reclaim/delete threads, block mapping (`bmap_has_holes`, `bmap_find`), and privilege/policy checks.

## Research Notes

This file is a control plane for operational and legacy features. The highest-risk paths are those that change mount-wide state (`ufs_fiosdio`, `ufs_fioffs`, `ufs_fiotune`) because they interact with lockfs, logging, clean flags, and background delete/reclaim threads.
