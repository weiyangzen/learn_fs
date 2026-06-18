# File Research: sources/os/linux/linux-stable/fs/nfs/proc.c

Purpose: Implements the NFSv2 client RPC operation table and the v2-specific glue between generic NFS/VFS operations and wire procedures.

Key responsibilities:
- Provides v2 handlers for `getroot`, `getattr`, `setattr`, `lookup`, `readlink`, create/remove/link/symlink/mkdir/rmdir/mknod, `readdir`, `statfs`, `fsinfo`, and `pathconf`.
- Builds `rpc_message` calls around `nfs_procedures[NFSPROC_*]`.
- Handles NFSv2 protocol quirks:
  - `mknod` is encoded through `CREATE`.
  - symlink creation receives no returned attributes/filehandle, so instantiation falls back to lookup.
  - no real COMMIT support; commit hooks are `BUG()`.
  - writes are always `NFS_FILE_SYNC`.
  - locks are bounded to 32-bit v2 offsets.
- Defines v2 inode operations and exports `nfs_v2_clientops`.

Integration:
- Used by the generic NFS client through `struct nfs_rpc_ops`.
- Calls into shared NFS helpers such as `nfs_instantiate`, `nfs_mark_for_revalidate`, `nfs_refresh_inode`, `nfs_writeback_update_inode`, and lockd via `nlmclnt_proc`.
- Supplies pageio setup/done hooks used by `read.c` and `write.c`.

Risks and notes:
- v2 lacks server-side delegation support; delegation hooks are stubs or force writeback.
- Root probing retries with the default RPC client when auth-specific client calls fail.
- Commit hooks intentionally must not be reached for v2.
