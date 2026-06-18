# File Research: sources/os/linux/linux-stable/fs/nfs/unlink.c

Purpose: Implements NFS sillyrename and deferred unlink handling for open-but-unlinked files.

Key responsibilities:
- Allocates `nfs_unlinkdata` for async deferred unlink operations.
- Marks dentries with `DCACHE_NFSFS_RENAMED` and stores unlink metadata in `d_fsdata`.
- Performs async unlink after the final dentry reference is dropped.
- Handles dentry alias races using `d_alloc_parallel` and transfers sillyrename metadata to matching aliases.
- Provides async rename helpers used by sillyrename.
- Generates hidden `.nfs<fileid><counter>` names and renames open files to those names before unlinking later.
- Cancels queued async unlink if the sillyrename RPC fails.

Integration:
- Uses protocol hooks `unlink_setup`, `unlink_rpc_prepare`, `unlink_done`, `rename_setup`, `rename_rpc_prepare`, and `rename_done`.
- Interacts with dcache lookup/aliasing, inode revalidation, lock semaphores, NFS delegation return, RPC async task machinery, and NFS stats/tracepoints.

Risks and notes:
- If sillyrename result is interrupted/unknown, it drops dentries and forces future lookup revalidation.
- Hidden sillyrename names are generated per fileid plus static counter and checked by negative lookup.
- Memory ownership is delicate: dentry refs, inode refs, credentials, superblock active refs, and `d_fsdata` all participate.
