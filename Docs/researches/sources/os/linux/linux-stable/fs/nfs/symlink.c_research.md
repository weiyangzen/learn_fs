# File Research: sources/os/linux/linux-stable/fs/nfs/symlink.c

Purpose: Implements NFS symlink inode operations and symlink target caching in the page cache.

Key responsibilities:
- `nfs_symlink_filler` calls the protocol `readlink` op into page zero and completes folio read state.
- `nfs_get_link` supports both RCU pathwalk and normal lookup:
  - RCU mode validates mapping and returns `-ECHILD` if it cannot safely use a cached uptodate folio.
  - non-RCU mode revalidates mapping and reads the symlink folio if needed.
- Exports `nfs_symlink_inode_operations` with `get_link`, `getattr`, and `setattr`.

Integration:
- Uses `NFS_PROTO(inode)->readlink`, NFS mapping revalidation, and VFS delayed calls via `page_put_link`.

Risks and notes:
- Symlink cache is single-folio/page-oriented, matching legacy NFS symlink target handling.
