# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_extern.h

Read completely: 160 lines.

Central external interface header for the ULFS layer inside NetBSD LFS. It forward-declares kernel structures and publishes vnode, directory, block mapping, quota, vfs, buffer-I/O, and snapshot entry points implemented across the `sys/ufs/lfs` ULFS files.

Major groups:
- Vnode operations: access, advlock, bmap, close, create, getattr, inactive, link, lookup, open, pathconf, print, readdir, readlink, remove, rmdir, setattr, strategy, whiteout, and special/fifo read/write/close variants.
- Block mapping: `ulfs_bmaparray()`, `ulfs_getlbns()`, and `ulfs_issequential_callback_t`.
- Inode helpers: `ulfs_reclaim()` and `ulfs_balloc_range()`.
- Directory helpers: `ulfs_dirbad()`, `ulfs_dirbadentry()`, `ulfs_direnter()`, `ulfs_dirremove()`, `ulfs_dirrewrite()`, `ulfs_dirempty()`, and `ulfs_blkatoff()`.
- Quota helpers: `ulfsquota_init()`, `ulfsquota_free()`, `lfs_chkdq()`, `lfs_chkiq()`, `lfsquota_handle_cmd()`, `lfs_qsync()`, quota1/quota2 unmount/mount functions.
- VFS helpers: init/reinit/done, start, root, quotactl, fhtovp.
- Vnode-init and I/O helpers: `ulfs_vinit()`, GOP allocation/update hooks, and `ulfs_bufio()`.
- Snapshot cleanup: `ulfs_snapgone()`.

Constants:
- `FORCE` is the shared quota-change flag allowing usage changes independent of limit enforcement.

Role:
- This header is the cross-module contract binding ULFS's vnode operation implementation to LFS-specific allocation, quota, and mount code.
