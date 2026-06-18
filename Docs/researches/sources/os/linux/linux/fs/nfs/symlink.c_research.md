# File Research: sources/os/linux/linux/fs/nfs/symlink.c

Implements NFS symlink page-cache handling and inode operations.

Key behavior:
- `nfs_symlink_filler()` reads symlink contents by invoking the protocol-specific `readlink` operation into the first page-cache folio.
- `nfs_get_link()` supports both RCU and non-RCU lookup:
  - RCU mode revalidates mapping through `nfs_revalidate_mapping_rcu()`, requires an existing uptodate folio, and returns `-ECHILD` when blocking work is required.
  - Non-RCU mode revalidates normally and uses `read_cache_folio()` with the filler to fetch the symlink target.
- Uses `set_delayed_call(done, page_put_link, folio)` so the VFS releases the folio after link resolution.
- Exports `nfs_symlink_inode_operations` with `.get_link`, `.getattr`, `.setattr`, and `.fileattr_get`.

Important interactions:
- Relies on the protocol table from `NFS_PROTO(inode)` for version-specific READLINK behavior.
- Uses the page cache as the symlink target cache, with revalidation delegated to generic NFS cache-validity helpers.
