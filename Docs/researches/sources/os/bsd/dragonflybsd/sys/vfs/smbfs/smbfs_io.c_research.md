# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_io.c

This file implements SMBFS data and directory I/O, including regular read/write paths, buffer-cache strategy I/O, VM pager getpages/putpages, and vnode buffer invalidation.

Directory reads are handled by `smbfs_readvdir`. It synthesizes `.` and `..`, maintains a per-node SMB find context in `n_dirseq`, reopens searches when the requested offset changes, advances through server search results with `smbfs_findnext`, and optionally does fast vnode prepopulation via `smbfs_nget`.

Regular reads in `smbfs_readvnode` validate vnode type and offset, invalidate cached buffers when remote mtime changes, then call `smb_read`. Writes in `smbfs_writevnode` handle append and sync cases, enforce `RLIMIT_FSIZE`, call `smb_write`, and update the vnode pager size when the file grows.

`smbfs_doio` translates buffer-cache reads/writes into single-segment `uio` SMB reads or writes. Read shortfalls are zero-filled. Writes clip dirty ranges to the known file size and preserve dirty/interrupted buffers for retry in some error paths.

The VM pager paths `smbfs_getpages` and `smbfs_putpages` map pages through a temporary pbuf KVA, build a `uio`, and issue SMB reads/writes. Because SMBFS closes FIDs on vnode close, these paths reopen the remote file when `n_opencount` is zero, then close it afterward. The comments call out race risks around concurrent opens.

`smbfs_vinvalbuf` serializes buffer invalidation with `NFLUSHINPROG`/`NFLUSHWANT`, retries `vinvalbuf`, supports interruptible waits, and clears `NMODIFIED` after successful invalidation.
