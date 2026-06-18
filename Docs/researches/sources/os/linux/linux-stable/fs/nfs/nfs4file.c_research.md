# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4file.c

This file defines NFSv4 file operations and wires NFSv4.2 file features into VFS operations when `CONFIG_NFS_V4_2` is enabled.

Core NFSv4 operations:
- `nfs4_file_open()`
  - Validates flags.
  - Allocates an NFS open context.
  - Handles truncate-on-open by flushing cached pages.
  - Calls NFS protocol `open_context()`.
  - Drops stale dentries on mismatch or selected lookup errors so VFS retries.
  - Sets open context and fscache state on success.
- `nfs4_file_flush()`
  - Flushes writeback and checks writeback errors.
  - If write delegation does not require flush-on-close, starts writeback only.
- `nfs4_setlease()` delegates lease handling to `nfs4_proc_setlease()`.

NFSv4.2 additions:
- `nfs4_copy_file_range()`
  - Attempts server-side copy, falls back to splice copy on unsupported or cross-device style errors.
- `__nfs4_copy_file_range()`
  - Requires NFSv4 file operations and copy capability on both files.
  - Uses synchronous copy for small copies.
  - For inter-server copy, obtains `COPY_NOTIFY` first.
  - Retries on `-EAGAIN`.
- `nfs4_file_llseek()`
  - Uses NFSv4.2 `SEEK` for `SEEK_HOLE` / `SEEK_DATA`, otherwise falls back to generic NFS llseek.
- `nfs42_fallocate()`
  - Supports allocate, punch-hole keep-size, and zero-range modes.
  - Checks regular file and new size.
  - Dispatches to allocate/deallocate/zero-range procedure wrappers.
- `nfs42_remap_file_range()`
  - Implements clone/remap via NFSv4.2 `CLONE`.
  - Rejects dedupe.
  - Validates clone block alignment.
  - Blocks direct I/O, syncs both inodes, calls clone RPC, and truncates destination page cache on success.
- Server-side-copy pseudo-open support:
  - `__nfs42_ssc_open()` creates a pseudo read-only file from a source filehandle and supplied stateid.
  - `__nfs42_ssc_close()` clears SSC state flags.
  - `nfs42_ssc_register_ops()` and `nfs42_ssc_unregister_ops()` register/unregister common SSC ops.

File operations table:
- `nfs4_file_operations` includes read/write, mmap prepare, open, flush, release, fsync, lock/flock, splice, flag checking, lease, and v4.2 copy/llseek/fallocate/remap hooks when enabled.

Risk areas:
- Open path intentionally returns `-EOPENSTALE` after dropping dentries so VFS retries correctly.
- Remap/clone must coordinate inode locking, direct I/O blocking, writeback synchronization, and destination cache invalidation.
- Server-side-copy pseudo-open manually constructs open state around a server-provided stateid; state flags must be reset on close.
