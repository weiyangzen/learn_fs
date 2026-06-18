# File Research: sources/os/linux/linux/fs/nfs/unlink.c

Implements NFS asynchronous unlink, asynchronous rename, and sillyrename handling for open-but-unlinked files.

Key behavior:
- `nfs_async_unlink()` allocates `nfs_unlinkdata`, copies the target name, captures current credentials, and stores the unlink data in `dentry->d_fsdata` while setting `DCACHE_NFSFS_RENAMED`.
- `nfs_complete_unlink()` clears the sillyrename flag, returns delegations/writeback as needed, then either starts the delayed unlink RPC or frees the queued unlink data if the inode is stale.
- Asynchronous unlink uses RPC callbacks to prepare the protocol-specific REMOVE call, process completion through `unlink_done`, restart when required, release dentry lookup state, drop superblock activity, and free data.
- `nfs_call_unlink()` protects against rmdir races with `rmdir_sem`, allocates a parallel dentry for the silly name, and transfers sillyrename data if lookup races reveal an existing alias.
- `nfs_async_rename()` builds and submits an asynchronous protocol-specific RENAME RPC with held dentries, directories, credentials, and post-op attribute buffers.
- Rename release marks affected inodes/directories for revalidation on uncertain results and releases held dentries, inodes, credentials, and superblock activity.
- `nfs_sillyrename()` creates hidden `.nfs<fileid><counter>` names, queues the final unlink first, runs the rename, waits for completion unless interrupted, updates verifiers and inode cache invalidation on success, and drops dentries on unknown restart results.

Important interactions:
- Handles stateless NFS open-file unlink semantics by preserving open files client-side until the last reference is dropped.
- Delegates protocol differences through `NFS_PROTO()->unlink_setup`, `unlink_rpc_prepare`, `unlink_done`, `rename_setup`, `rename_rpc_prepare`, and `rename_done`.
- Uses dentry flags and `d_fsdata` as the durable handoff between unlink-time sillyrename setup and final dentry release.
