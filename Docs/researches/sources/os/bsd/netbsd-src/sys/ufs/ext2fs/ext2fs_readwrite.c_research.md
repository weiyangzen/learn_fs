# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_readwrite.c

This file implements ext2fs read and write vnode operations for regular files plus buffer-cache read/write helpers for directories and long symlinks. It bridges ext2fs block sizing with NetBSD UBC, buffer cache, timestamp updates, and inode size consistency.

Key responsibilities:
- Read regular files through UBC.
- Read directories and long symlinks through the buffer cache.
- Write regular files through UBC after reserving blocks with `ufs_balloc_range`.
- Write directories and long symlinks through `ext2fs_balloc`.
- Update access/change/modify timestamps and enforce setuid/setgid clearing after writes.
- Roll back file size on write errors.

Important functions:
- `ext2fs_read`: Validates regular-file or directory reads. Directory reads are delegated to `ext2fs_bufrd`; regular-file reads use `ubc_uiomove` with `UBC_READ`, bounded by `ext2fs_size`.
- `ext2fs_bufrd`: Buffer-cache read path for directories and long symlinks. It maps offsets to ext2 logical blocks, uses `bread` or `breadn` for simple readahead, handles short buffers conservatively, and copies data with `uiomove`.
- `ext2fs_post_read_update`: Sets `IN_ACCESS` unless `MNT_NOATIME`; performs synchronous inode update for `IO_SYNC`. Original read errors override timestamp update errors.
- `ext2fs_write`: Handles append semantics and ext2 append-only enforcement, checks maximum file size, allocates ranges, copies via UBC, updates UVM vnode size, and flushes pages for synchronous or non-async writes.
- `ext2fs_bufwr`: Buffer-cache write path for directories and long symlinks. It allocates blocks with `ext2fs_balloc`, extends inode size as needed, writes data with `uiomove`, and chooses `bwrite`, `bawrite`, or `bdwrite`.
- `ext2fs_post_write_update`: Sets ctime/mtime and optionally atime under `MNT_RELATIME`, clears privileged mode bits when credentials lack retention authority, truncates back on write error, and synchronously updates metadata for `IO_SYNC`.

Important interactions:
- Uses `ext2fs_balloc`, `ext2fs_setsize`, `ext2fs_truncate`, `ext2fs_update`, and UFS buffer I/O conventions.
- Regular-file allocation is through shared UFS `ufs_balloc_range`, while buffer-cache writes use ext2fs-specific `ext2fs_balloc`.

Notable behavior and risks:
- The write path temporarily uses UVM write size before allocation/copy and asserts final vnode size equals ext2 inode size.
- In `ext2fs_post_write_update`, the setuid clearing branch uses `ip->i_e2fs_mode &= ISUID` when authorization fails. This preserves only the setuid bit rather than clearing it, unlike the setgid branch which uses `&= ~ISGID`; this looks suspicious and should be reviewed against upstream intent.
- Error recovery restores `uio_offset` and `uio_resid` to pre-write values and truncates to the original size.
