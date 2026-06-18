# File Research: sources/os/linux/linux/fs/nfs/nfs4file.c

This file defines NFSv4 file operations and wires NFSv4.2 file features into VFS operations when `CONFIG_NFS_V4_2` is enabled.

Core NFSv4 operations:
- `nfs4_file_open()` validates flags, strips create/exclusive flags, allocates an NFS open context, handles truncate-on-open by flushing cached pages, calls the protocol `open_context()` operation, drops stale dentries on selected lookup errors, installs the open context, opens fscache state, and enables direct I/O capability.
- `nfs4_file_flush()` flushes dirty writeback and reports writeback errors on close. If a write delegation does not require flush-on-close, it starts writeback without waiting for completion.
- `nfs4_setlease()` delegates lease handling to `nfs4_proc_setlease()`.

NFSv4.2 additions:
- `__nfs4_copy_file_range()` tries server-side copy only for NFSv4 file operations and copy-capable servers. It selects synchronous copy for small ranges, performs `COPY_NOTIFY` for inter-server copy, and retries `-EAGAIN`.
- `nfs4_copy_file_range()` falls back to `splice_copy_file_range()` for unsupported or cross-device style failures.
- `nfs4_file_llseek()` uses NFSv4.2 `SEEK` for `SEEK_HOLE` and `SEEK_DATA`, falling back to generic NFS seek when unsupported.
- `nfs42_fallocate()` supports allocate, punch-hole-keep-size, and zero-range modes for regular files, validates new size, and dispatches to NFSv4.2 procedure wrappers.
- `nfs42_remap_file_range()` implements clone/remap via `CLONE`, rejects dedupe and unsupported flags, validates clone block alignment, blocks direct I/O, syncs both inodes, calls clone RPC, and invalidates destination page cache on success.
- Server-side-copy pseudo-open helpers create and close read-only pseudo files around a source filehandle and server-provided stateid for inter-server copy support.

File operations table:
- `nfs4_file_operations` binds read/write, mmap prepare, open, flush, release, fsync, locks, splice, flag checking, leases, and, under NFSv4.2, copy, llseek, fallocate, and remap hooks.
- The table sets `FOP_DONTCACHE`.

Risk areas:
- Open path intentionally returns `-EOPENSTALE` after dropping dentries so VFS retries lookup/open correctly.
- Clone/remap must coordinate inode locking, direct I/O blocking, writeback synchronization, and destination cache invalidation.
- Server-side-copy pseudo-open manually constructs open state around a server-provided stateid and clears state flags on close.
