# File Research: sources/os/linux/linux/fs/orangefs/inode.c

Implements OrangeFS address-space operations, inode attribute operations, inode instantiation, and file attribute ioctls.

Key behavior:
- Writeback tracks dirty byte ranges per folio in `orangefs_write_range`, including uid/gid, so writeback can preserve credentials and coalesce adjacent ranges.
- `orangefs_writepages()` batches compatible dirty folios into one `wait_for_direct_io(WRITE)` transfer up to bufmap slot size.
- `orangefs_readahead()` may expand large readahead windows, reads through shared-memory direct I/O, and marks folios uptodate.
- `orangefs_read_folio()` reads one folio via direct I/O, zeros unread tail through the iterator, flushes dcache, and ends the folio read.
- `orangefs_write_begin()` attaches/extends private write ranges or launders incompatible dirty folios.
- `orangefs_write_end()` updates inode size, handles short-copy zeroing, marks dirty, and schedules inode metadata sync.
- `orangefs_invalidate_folio()` trims or drops private write ranges on invalidation; unsupported punched-middle cases warn.
- `orangefs_direct_IO()` chunks iterator I/O by bufmap size, updates offsets, access time, mtime, and inode size.
- `orangefs_page_mkwrite()` attaches full-page write ranges for mmap writes and marks folios dirty under pagefault accounting.
- `orangefs_setattr_size()` refreshes size, adjusts page cache/i_size, sends `ORANGEFS_VFS_OP_TRUNCATE`, and marks time attrs when size changes.
- `__orangefs_setattr()` rejects unsupported sticky/setuid cases, records pending attrs/credentials in private inode state, copies attrs locally, and marks inode dirty for later server setattr.
- `orangefs_getattr()` refreshes OrangeFS attrs and fills VFS stat data.
- `orangefs_permission()` refreshes attrs before generic permission checks.
- `orangefs_fileattr_get/set()` maps Linux file flags to `user.pvfs2.meta_hint` xattr with limited supported flags.
- `orangefs_iget()` uses `iget5_locked()` keyed by OrangeFS fsid/handle and fetches attrs for new inodes.
- `orangefs_new_inode()` creates new VFS inodes for server-created objects, applies inherited ACLs, initializes ops, and inserts into inode hash.

Important tables:
- `orangefs_address_operations` supplies readahead/read/write/invalidate/release/free/migrate/launder/direct-IO.
- File inode operations include ACL, setattr/getattr, xattr list, permission, time update, and fileattr get/set.
