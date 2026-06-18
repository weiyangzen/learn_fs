# File Research: sources/os/linux/linux-stable/fs/autofs/inode.c

## Purpose
Implements autofs superblock setup, mount option parsing, inode allocation, teardown, and mount option display.

## Main Interfaces
- `autofs_init_fs_context()`.
- `autofs_get_inode()`.
- `autofs_new_ino()`, `autofs_clean_ino()`, `autofs_free_ino()`.
- `autofs_kill_sb()`.

## Important Behavior
Mount parsing accepts daemon pipe fd, uid/gid, owner process group, protocol min/max, mount type flags, strict-expire, and ignore. The pipe is opened during parse to avoid fd reuse races and is forced into packet-pipe mode.

`autofs_alloc_sbi()` initializes catatonic state, protocol defaults, locks, active/expiring lists, mount namespace id, and default indirect type. `autofs_validate_protocol()` negotiates protocol version/subversion. `autofs_fill_super()` creates the root inode/dentry, attaches root `autofs_info`, assigns daemon process group, marks trigger roots managed when needed, and leaves catatonic mode.

`autofs_kill_sb()` enters catatonic mode to release waiters and close the pipe, drops the daemon pgrp, kills the anonymous superblock, and RCU-frees `sbi`.

## Cross-File Relationships
Provides state consumed by `root.c`, `waitq.c`, `expire.c`, and `dev-ioctl.c`. Inode operation tables are defined in `root.c` and `symlink.c`.

## Risks / Review Notes
Several mount options affect ABI-visible protocol behavior. Error paths during `autofs_fill_super()` must avoid leaking `autofs_info`, pipe refs, and pgrp refs. `autofs_evict_inode()` frees symlink target storage from `i_private`.
