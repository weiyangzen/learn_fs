# File Research: sources/os/linux/linux-stable/fs/orangefs/inode.c

## Scope

This file implements OrangeFS inode and address-space operations: buffered read/write, readahead, writeback batching, mmap page dirtying, direct I/O, setattr/getattr/permission/time/fileattr operations, inode lookup, and new inode creation.

## APIs Covered

- Address-space ops: `orangefs_readahead()`, `orangefs_read_folio()`, `orangefs_write_begin()`, `orangefs_write_end()`, `orangefs_writepages()`, invalidate/release/free/launder folio, `orangefs_direct_IO()`.
- mmap dirtying: `orangefs_page_mkwrite()`.
- Metadata: `orangefs_setattr()`, `__orangefs_setattr()`, `orangefs_setattr_size()`, `orangefs_getattr()`, `orangefs_permission()`, `orangefs_update_time()`.
- File attributes: `orangefs_fileattr_get()`, `orangefs_fileattr_set()`.
- Inode lifecycle: `orangefs_init_iops()`, `orangefs_iget()`, `orangefs_new_inode()`.

## Control Flow And Behavior

- Dirty folios carry `struct orangefs_write_range` private data recording byte range and credentials; writeback uses those ranges rather than blindly writing whole pages.
- `orangefs_writepages()` batches contiguous dirty ranges with matching uid/gid up to bufmap size, then sends them through `wait_for_direct_io()`.
- Readahead may expand large reads and transfers data in chunks up to 4 MiB through daemon shared buffers.
- `read_folio` launders dirty folios first, reads from daemon, zeroes unread portions, flushes dcache, and completes the folio.
- `write_begin` extends or replaces folio private write ranges, laundering if dirty state is incompatible.
- `write_end` updates `i_size`, zeroes short-copy stale ranges, marks dirty, unlocks/releases folio, and marks inode dirty.
- `page_mkwrite` attaches or updates a full-page write range, updates timestamps, marks dirty before returning a locked folio.
- Truncate refreshes size, adjusts page cache and `i_size`, sends TRUNCATE op, and updates ctime/mtime validity when size changed.
- `__orangefs_setattr()` rejects unsupported sticky/setuid cases, accumulates attribute updates with credential ownership, updates inode fields, and marks inode dirty.
- `orangefs_iget()` uses `iget5_locked()` keyed by OrangeFS fsid/handle; new inodes fetch attributes before installing operations.
- `orangefs_new_inode()` creates ACLs, fetches attributes, installs operations, writes default/access ACLs, inserts inode into hash, and reconciles mode.

## Risks And Invariants

- Folio private write ranges and credentials must stay consistent across invalidation, laundering, mmap writes, and batched writeback.
- Mapping invalidation is coordinated with `orangefs_revalidate_mapping()` bitlock.
- Fileattr flags are stored in `user.pvfs2.meta_hint`; only immutable, append, noatime, and internal mirror bit handling are allowed.
- Inode identity uses full OrangeFS handles for equality; inode number is a hash of the handle and can collide.
- Attribute writeback may force `write_inode_now()` when current credentials differ from accumulated attr credentials.
