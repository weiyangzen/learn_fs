# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_io.c

## Purpose

Implements SMBFS file, directory, buffer-cache, and VM pager I/O helpers.

## Main Entry Points

Directory reads:
- `smbfs_readvdir()` emits `.` and `..`, opens or reuses a server search context, advances to the requested directory offset, reads entries via `smbfs_findnext()`, optionally performs fast vnode lookup/cache entry creation, and maps `ENOENT` to EOF.

File reads/writes:
- `smbfs_readvnode()` rejects unsupported segment modes and vnode types, handles directory reads, invalidates buffers if cached mtime changed, and reads from the open SMB fid with `smb_read()`.
- `smbfs_writevnode()` handles append/sync invalidation, enforces file-size limits with `vn_rlimit_fsize()`, writes with `smb_write()`, updates cached size, and adjusts pager size.

Buffer and pager I/O:
- `smbfs_doio()` maps a `struct buf` to a kernel `uio` and issues `smb_read()` or `smb_write()`, zero-filling short reads and preserving dirty buffers on interrupted or commit-needed writes.
- `smbfs_getpages()` maps VM pages into a pbuf, reads file data into them, and marks valid ranges.
- `smbfs_putpages()` maps dirty pages and writes them synchronously, then undirties pages on success.
- `smbfs_vinvalbuf()` serializes buffer flush/invalidate with `NFLUSHINPROG`/`NFLUSHWANT`, cleans vnode pages, retries `vinvalbuf()`, and handles interruptible waits.

## Integration Points

Called by SMBFS vnode operations for read/write/readdir/strategy/getpages/putpages and by node inactivity/close paths. It depends on `netsmb` `smb_read()`/`smb_write()`, SMB credentials, search contexts from `smbfs_smb.c`, and node cache fields.

## Risks and Review Notes

The directory offset model is `sizeof(struct dirent)` slots and maintains a single `n_dirseq` search context per node, so seek patterns can cause search reopen/skip work.

The buffer-write comment references NFS commit flags, reflecting inherited/old buffer-cache logic. Interrupted writes and dirty buffer preservation should be regression-tested for SMBFS specifically.
