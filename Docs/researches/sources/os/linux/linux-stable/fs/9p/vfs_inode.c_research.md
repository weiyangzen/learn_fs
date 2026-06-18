# File Research: sources/os/linux/linux-stable/fs/9p/vfs_inode.c
- Purpose: Implements legacy/dotu 9P inode operations and common inode conversion logic.
- Main functions: mode conversion helpers, `v9fs_alloc_inode`, `v9fs_init_inode`, `v9fs_evict_inode`, `v9fs_inode_from_fid`, `v9fs_create`, `v9fs_vfs_lookup`, `v9fs_vfs_atomic_open`, unlink/rmdir/rename/getattr/setattr/symlink/link/mknod helpers, `v9fs_stat2inode`, `v9fs_refresh_inode`.
- Protocol conversion: Maps Unix modes/open flags to 9P modes and maps 9P stat metadata back into Linux inode state.
- Create/open path: Uses parent FIDs and `p9_client_create`/walk operations, instantiates or reuses inodes based on cache policy, and attaches FIDs to dentries/files.
- Metadata path: Uses `p9_client_stat`/`p9_client_wstat`; invalidates cached inode attributes after modifications.
- Operation tables: Provides legacy and dotu directory/file/symlink inode operations with dotu-only symlink/link handling.
- Risks: Rename serializes through `rename_sem`; cached versus uncached inode instantiation changes alias behavior; writeback/fscache resizing must stay synchronized with remote size changes.
