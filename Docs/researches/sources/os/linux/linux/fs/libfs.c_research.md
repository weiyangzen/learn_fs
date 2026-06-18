# File Research: sources/os/linux/linux/fs/libfs.c

Purpose: General VFS helper library for simple/pseudo filesystems, directory iteration, page-cache-backed in-memory files, transaction attributes, export file handles, casefolding/encryption dentry ops, inode versioning, direct-I/O fallback, and stashed anonymous dentries.

Major helper families:
- Basic stat/lookup/directory helpers: `simple_getattr()`, `simple_statfs()`, `simple_lookup()`, `simple_dir_operations`, `dcache_readdir()`.
- Stable directory offsets: `simple_offset_*`, `simple_offset_dir_operations`, and maple-tree-backed offset assignment/removal/rename support.
- Recursive removal: `simple_recursive_removal()`, `locked_recursive_removal()`, and `simple_remove_by_name()`.
- Pseudo filesystem setup: `init_pseudo()`, `pseudo_fs_fill_super()`, and pseudo fs_context operations.
- Simple inode operations: link, unlink, rmdir, rename, setattr, empty-dir helpers, symlink helpers, anonymous inode allocation.
- Ram/page-cache helpers: `ram_aops`, `simple_write_begin()`, `simple_write_end()`, `simple_fill_super()`.
- Buffer helpers: `simple_read_from_buffer()`, `simple_write_to_buffer()`, `memory_read_from_buffer()`.
- Transaction and simple attribute helpers: `simple_transaction_*`, `simple_attr_*`.
- Exportfs helpers: `generic_encode_ino32_fh()`, `generic_fh_to_dentry()`, `generic_fh_to_parent()`.
- Sync/addressability: `simple_fsync_noflush()`, `simple_fsync()`, `generic_check_addressable()`, `noop_fsync()`, `noop_direct_IO()`.
- Casefold/encryption: `generic_ci_d_compare()`, `generic_ci_d_hash()`, `generic_ci_match()`, `generic_set_sb_d_ops()`.
- I_version and I/O fallback: `inode_maybe_inc_iversion()`, `inode_query_iversion()`, `direct_write_fallback()`.
- Stashed dentries: `stashed_dentry_get()`, `stash_dentry()`, `path_from_stashed()`, `stashed_dentry_prune()` for nsfs/pidfs-style paths.

Dependencies and integration:
- Exports many symbols used by in-kernel filesystems, including kernfs (`ram_aops`, simple xattr/stat helpers), procfs-like files, pseudo filesystems, and exportfs clients.
- Uses VFS dentries/inodes, maple tree, fscrypt, Unicode casefolding, writeback, block flush, and mount/fs_context APIs.

Concurrency and risk notes:
- Directory iteration relies on dentry locks, inode rwsem, cursor dentries, and rescheduling-safe scans.
- Offset maps require caller serialization for rename/remove paths.
- Transaction files allow only one write per open and use a static spinlock to serialize `private_data` installation.
- I_version helpers rely on explicit memory barriers paired between query and increment paths.
- `direct_write_fallback()` must preserve O_DIRECT semantics by writing back and invalidating buffered fallback ranges.
