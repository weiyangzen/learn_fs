# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_lockfs.h

## Role

Defines UFS lockfs state, masks, flags, and helpers for filesystem quiescing and operation blocking.

## Lock Types and Behavior

The file documents UFS lockfs modes:
- unlock
- name lock
- write lock
- delete lock
- hard lock
- error lock
- read-only error lock placeholder

Most vnode operations increment `ul_vnops_cnt` on entry and decrement on exit; a filesystem is quiescent when this count reaches zero. Some operations do not obey the protocol, including close, putpage, inactive, addmap/delmap, rwlock/rwunlock, and poll.

## Key Definitions

- `ULOCKFS_BUSY`, `ULOCKFS_NOIACC`, `ULOCKFS_NOIDEL`, `ULOCKFS_FALLOC`.
- Lock bit masks: `ULOCKFS_ULOCK`, `WLOCK`, `NLOCK`, `DLOCK`, `HLOCK`, `ELOCK`, `ROELOCK`, `FWLOCK`, `SLOCK`.
- Per-operation masks for read, write, getattr, setattr, access, lookup, create, remove, link, rename, mkdir/rmdir, readdir, symlink, fsync, space/fallocate, quota, getpage, map, ioctl paths, vget, and delete.

## Main Structure

`struct ulockfs` stores flags, current lock state, modification marker, active vnode operation count, mutex/CV, superblock-owner thread, user-visible `struct lockfs`, and fallocate count.

## Integration Notes

Includes `ufs_trans.h` and maps vnodes/inodes to `ulockfs` through `VTOUL()` and `ITOUL()`. Exports `ufs_quiesce_pend`.

## Risk Notes

Masks encode policy for every UFS operation. Incorrect masks can allow mutation during freeze/error handling or unnecessarily block safe operations.
