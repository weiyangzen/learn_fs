# File Research: sources/os/linux/linux-stable/fs/libfs.c

Large VFS helper library for simple/pseudo filesystems, in-memory directory operations, offset-stable directory iteration, recursive removal, simple file operations, xattrs-adjacent helpers, export file handles, casefold/encryption dentry ops, i_version, direct-I/O fallback, and stashed anonymous paths.

Major helper families:
- Basic helpers: `simple_getattr()`, `simple_statfs()`, `simple_lookup()`, `generic_read_dir()`, `noop_fsync()`, `kfree_link()`.
- Dcache-backed directories: `dcache_dir_open/close/lseek`, `dcache_readdir()`, `simple_dir_operations`, and `simple_dir_inode_operations`.
- Offset directories: `simple_offset_init/add/remove/rename/rename_exchange/destroy()` use maple trees and `d_fsdata` to assign stable readdir offsets.
- Recursive removal: `simple_recursive_removal()`, `locked_recursive_removal()`, and `simple_remove_by_name()` walk positive children, invalidate dentries, update nlinks/timestamps, and invoke optional callbacks.
- Pseudo filesystem setup: `init_pseudo()` installs fs_context ops for non-user-mountable pseudo filesystems.
- Simple inode/dentry mutations: `simple_link()`, `simple_empty()`, `simple_unlink()`, `simple_rmdir()`, `simple_rename_timestamp()`, `simple_rename()`, `simple_setattr()`.
- Ramfs-style pagecache data: `ram_aops` with zero-fill read folio, `simple_write_begin()`, and `simple_write_end()`.
- Superblock filling and pinning: `simple_fill_super()`, `simple_pin_fs()`, and `simple_release_fs()`.
- Buffer helpers: `simple_read_from_buffer()`, `simple_write_to_buffer()`, and `memory_read_from_buffer()`.
- Transaction files: `simple_transaction_get/set/read/release()`.
- Simple numeric attrs: `simple_attr_open/read/write/write_signed/release()`.
- Export helpers: `generic_encode_ino32_fh()`, `generic_fh_to_dentry()`, `generic_fh_to_parent()`.
- Fsync and addressability: `simple_fsync_noflush()`, `simple_fsync()`, `generic_check_addressable()`.
- Anonymous inodes and fast symlinks: `alloc_anon_inode()`, `simple_get_link()`, `simple_symlink_inode_operations`.
- Empty dirs: `make_empty_dir_inode()` and `is_empty_dir_inode()`.
- Casefold/encryption: `generic_ci_d_compare()`, `generic_ci_d_hash()`, `generic_ci_match()`, `generic_set_sb_d_ops()`.
- i_version: `inode_maybe_inc_iversion()` and `inode_query_iversion()` use atomic cmpxchg and paired memory barriers.
- Direct-I/O fallback: `direct_write_fallback()` reconciles partial direct writes with buffered fallback and invalidates page cache.
- Stashed paths: `stashed_dentry_get()`, `stash_dentry()`, `path_from_stashed()`, `stashed_dentry_prune()` support nsfs/pidfs-style reusable anonymous dentries.
- Creation helpers: `simple_start_creating()` and `simple_done_creating()` wrap lookup/create locking.

Concurrency notes:
- Directory scanning uses dentry locks and cursor dentries.
- Offset directories rely on caller-held `i_rwsem`.
- `simple_pin_fs()` uses a spinlock-protected mount/count pair.
- Stashed dentries use RCU, lockref, and cmpxchg to avoid stale dead dentry reuse.
