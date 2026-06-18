# File Research: sources/os/linux/linux-stable/fs/ext4/file.c

This file implements regular-file VFS operations for ext4: read, write, splice read, mmap preparation, open/release, llseek, and the exported file/inode operation tables.

Major responsibilities:
- Read path:
  - `ext4_file_read_iter()` rejects forced shutdown, skips zero-length atime updates, chooses DAX, direct I/O, or buffered read.
  - `ext4_dio_read_iter()` uses iomap direct I/O under shared inode lock and falls back to buffered I/O when ext4 features do not support DIO.
  - `ext4_dax_read_iter()` uses DAX iomap when DAX remains valid under inode lock.
  - `ext4_file_splice_read()` checks forced shutdown then delegates to `filemap_splice_read()`.
- Write path:
  - `ext4_file_write_iter()` checks emergency state, handles DAX, validates atomic write size, and selects direct or buffered write.
  - `ext4_buffered_write_iter()` performs generic buffered writes under exclusive inode lock and syncs as needed.
  - `ext4_dio_write_iter()` manages direct I/O, fallback to buffered completion, orphan handling for extension, lock sharing, and page-cache invalidation after fallback.
  - `ext4_dax_write_iter()` handles DAX writes, extension orphaning, inode size update, and sync.
- Direct I/O policy:
  - `ext4_should_use_dio()` implements ext4’s historical behavior: feature-unsupported DIO falls back to buffered I/O, but misaligned DIO for otherwise DIO-capable files is left to DIO to reject.
  - `ext4_dio_write_checks()` decides shared vs exclusive inode lock, handles NOWAIT, extending writes, unaligned writes, overwrite checks, security-time updates, DIO drain, and `IOMAP_DIO_FORCE_WAIT`.
  - `ext4_dio_write_end_io()` converts unwritten extents after DIO, including the atomic-write conversion path, and extends inode size if needed.
- Extension cleanup:
  - `ext4_handle_inode_extension()` updates inode size and removes orphan tracking when the full intended write completed.
  - `ext4_inode_extension_cleanup()` truncates failed extension writes or removes stale orphan tracking after races.
- mmap:
  - DAX faults use `ext4_dax_huge_fault()` / `ext4_dax_fault()` with journal handling for shared write faults, invalidate locking, ENOSPC retry, and synchronous fault completion.
  - `ext4_file_mmap_prepare()` checks shutdown/emergency state, validates synchronous mapping support, installs DAX or buffered vm ops, and enables huge pages for DAX.
- Open/release:
  - `ext4_file_open()` samples last mounted path, runs fscrypt/fsverity open checks, attaches a JBD2 inode for writers, enables atomic-write capability when supported, and advertises NOWAIT/ODIRECT.
  - `ext4_release_file()` flushes delayed allocation on close, discards preallocations for the last writer, and frees htree directory private state.
- Seeking:
  - `ext4_llseek()` uses iomap SEEK_DATA/SEEK_HOLE reporting and selects max file size based on extents vs indirect mapping.
- Operation tables:
  - `ext4_file_operations` wires llseek, read/write, iopoll, ioctls, mmap, open/release, fsync, splice, fallocate, lease, and feature flags.
  - `ext4_file_inode_operations` wires setattr/getattr, xattrs, ACLs, fiemap, and file attributes.

Important design points:
- Extending direct/DAX writes use orphan tracking so crashes do not expose partially extended files.
- Unaligned direct writes to unwritten or non-overwrite regions require exclusive locking and DIO draining to avoid partial-block zeroing races.
- Direct I/O fallback to buffered I/O flushes and invalidates the affected page-cache range to preserve DIO semantics.
- Atomic writes are DIO-only and constrained by superblock atomic write unit bounds.
- DAX mmap write faults journal metadata only for shared writable faults, not private COW faults.

Key invariants:
- Forced shutdown returns `-EIO`; emergency state blocks writes.
- Buffered writes do not support `IOCB_NOWAIT`.
- DIO writes must clear `EXT4_STATE_MAY_INLINE_DATA` before allocating blocks.
- Non-extent files are capped at `s_bitmap_maxbytes`.
- DAX vm ops are installed only when the mapping and dax device support the requested semantics.
