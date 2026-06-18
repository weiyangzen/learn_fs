# File Research: sources/os/linux/linux/fs/ext4/file.c

Implements ext4 regular-file operations: reads, writes, mmap, open/release, llseek, and file/inode operation tables.

Key behavior:
- `ext4_should_use_dio()` preserves ext4 direct-I/O behavior:
  - unsupported ext4 features fall back to buffered I/O
  - misaligned DIO for otherwise supported files is attempted so iomap can return `EINVAL`
- Read path:
  - rejects forced shutdown
  - skips atime work for zero-length reads
  - routes DAX reads to `dax_iomap_rw()`
  - routes direct reads to `iomap_dio_rw()`
  - otherwise uses generic buffered reads
- `ext4_file_splice_read()` rejects forced shutdown and delegates to `filemap_splice_read()`.
- `ext4_release_file()` flushes delayed allocation close state, discards preallocations for the last writer, and frees htree directory private data if present.
- Write checks enforce immutability, generic write limits, non-extent bitmap max size, timestamp/security updates, and stale-data EOF zeroing for writes beyond EOF.
- Buffered writes lock the inode exclusively and use `generic_perform_write()`.
- Direct writes:
  - choose shared vs exclusive inode locking based on extending writes, overwrite status, unaligned I/O, unwritten extents, and security updates
  - drain outstanding DIO when partial-block zeroing could corrupt concurrent I/O
  - add the inode to the orphan list for extending writes
  - convert unwritten extents at end I/O, including the atomic-write conversion path
  - clean up orphan/truncate state after synchronous extending DIO
  - can fall back to buffered I/O for remaining data and then writeback/invalidate the affected page-cache range
- Atomic writes validate write unit bounds and generic atomic-write constraints before DIO.
- DAX write path uses exclusive locking, orphan protection for extending writes, `dax_iomap_rw()`, and inode extension cleanup.
- DAX fault path starts a journal handle for shared writable faults, handles ENOSPC retries, and completes synchronous DAX faults.
- `ext4_file_mmap_prepare()` validates emergency/forced-shutdown state, DAX synchronous mapping support, and installs DAX or buffered vm ops.
- `ext4_sample_last_mounted()` opportunistically records the current mount path into the superblock.
- `ext4_file_open()` validates shutdown state, samples mount path, runs fscrypt/fsverity open checks, attaches a JBD2 inode for writers, marks atomic-write capability, and delegates quota open handling.
- `ext4_llseek()` supports generic seeks plus `SEEK_HOLE` and `SEEK_DATA` through iomap report ops.
- Defines `ext4_file_operations` and `ext4_file_inode_operations`.

Important interactions:
- Relies on iomap for DIO, DAX, and hole/data seeking.
- Coordinates orphan list, unwritten extent conversion, inode size, and `i_disksize` for crash-safe extending writes.
- Operation tables connect this file to ioctl, fallocate, fsync, xattrs, ACLs, fiemap, and file attributes.
