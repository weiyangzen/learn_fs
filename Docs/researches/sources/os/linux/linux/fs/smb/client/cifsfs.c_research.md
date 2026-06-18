# File Research: sources/os/linux/linux/fs/smb/client/cifsfs.c

## Purpose
`cifsfs.c` is the main Linux VFS integration and module lifecycle file for the CIFS/SMB3 client. It defines module parameters/globals, filesystem types, superblock operations, inode/file/dir operation tables, mount setup, copy/clone operations, memory pools, workqueues, and module init/exit.

## Main Responsibilities
- Defines module-wide knobs:
  - buffer sizes and pool minimums,
  - pending request limits,
  - directory cache timeout,
  - oplock/signing/encryption dialect behavior toggles,
  - legacy dialect restrictions.
- Owns global counters and locks for XIDs, sessions, tcons, TCP sessions, buffers, and mids.
- Implements superblock setup and teardown.
- Registers `cifs` and `smb3` filesystem types.
- Exposes inode/file/directory operation tables to VFS.
- Integrates with netfs/fscache, pagecache invalidation, and server-side copy offload.
- Initializes and destroys request buffers, inode cache, mid pool, IO request pools, workqueues, DFS/SPNEGO/SWN/idmap support, and proc state.

## Important Functions
- `cifs_sb_active()` / `cifs_sb_deactive()`: manage CIFS superblock active references.
- `cifs_read_super()`: initializes a superblock, root inode, dentry ops, bdi/readahead settings, time granularity, xattrs, export ops, and max file size.
- `cifs_kill_sb()`: closes cached dirs/deferred files, flushes workqueues, releases root, kills anon super, and unmounts CIFS state.
- `cifs_statfs()`: builds path and dispatches `server->ops->queryfs`.
- `cifs_fallocate()`: serializes with inode lock, waits for netfs IO, marks file modified, dispatches protocol fallocate op.
- `cifs_permission()`: honors `noperm` mount behavior or falls back to generic permission checks.
- `cifs_alloc_inode()` / `cifs_free_inode()` / `cifs_evict_inode()`: manage CIFS inode lifecycle and netfs/fscache teardown.
- `cifs_show_options()`: renders mount options for `/proc/mounts`.
- `cifs_get_root()`: resolves prefix-path mounts to the actual root dentry.
- `cifs_smb3_do_mount()`: duplicates fs context, mounts server/share, gets or creates superblock, reads superblock, and returns mounted root.
- `cifs_llseek()`: revalidates remote size for `SEEK_END`, `SEEK_DATA`, and `SEEK_HOLE`.
- `cifs_setlease()`: gates VFS leases on CIFS oplock/cache state.
- `cifs_fileattr_get()`: reports compression and casefold/case-preserving attributes.
- `cifs_remap_file_range()`: implements clone/duplicate-extents path with source flush, EOF adjustment, destination folio flush/invalidate, fscache invalidation, and size updates.
- `cifs_file_copychunk_range()` / `cifs_copy_file_range()`: implement server-side copychunk with splice fallback.
- `init_cifs()` / `exit_cifs()`: module load/unload lifecycle.

## VFS Operation Tables
- Filesystem types:
  - `cifs_fs_type`
  - `smb3_fs_type`
- Super operations:
  - `cifs_super_ops`
- Inode operations:
  - `cifs_dir_inode_ops`
  - `cifs_file_inode_ops`
  - `cifs_symlink_inode_ops`
- File operations:
  - `cifs_file_ops`
  - `cifs_file_strict_ops`
  - `cifs_file_direct_ops`
  - `cifs_file_nobrl_ops`
  - `cifs_file_strict_nobrl_ops`
  - `cifs_file_direct_nobrl_ops`
  - `cifs_dir_ops`

## Initialization Order
`init_cifs()` initializes, in order:
1. SMB1/SMB2 error maps.
2. proc entries and global counters.
3. workqueues.
4. inode cache.
5. netfs IO pools.
6. MID pool.
7. request buffer pools.
8. DFS cache, SPNEGO, SWN genl when configured.
9. CIFS idmap.
10. `cifs` and `smb3` filesystem registration.

The error path unwinds each initialized component in reverse order.

## Caching and IO Notes
- Superblock readahead is derived from negotiated or requested `rsize`.
- Inodes embed `struct netfs_inode`.
- Copy/clone operations flush source ranges and invalidate destination cache/fscache before server-side mutation.
- Oplock/cache state affects leases and seek revalidation behavior.
- `cifs_evict_inode()` waits for outstanding netfs IO and releases fscache cookies.

## Safety and Concurrency Notes
- Workqueues are flushed during forced superblock teardown to finish oplock/deferred close work.
- `cifs_umount_begin()` wakes request/response wait queues for forced unmount progress.
- `cifs_remap_file_range()` locks both non-directory inodes and handles overlapping/unsupported clone cases.
- Module parameter values are range-clamped during initialization.
