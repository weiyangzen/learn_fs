# File Research: sources/os/linux/linux/fs/ocfs2/dlmfs/userdlm.h

## Purpose
Declares the internal dlmfs userspace-DLM data structures, constants, and function interfaces shared by `dlmfs.c` and `userdlm.c`.

## Key Definitions
- `USER_DLM_LOCK_ID_MAX_LEN` is 32.
- `DLMFS_MAGIC` is `0x76a9f425`.
- `user_lock_res` is the core per-lock state object:
  - spinlock and flags;
  - lock name and name length;
  - granted level;
  - PR/EX holder counts;
  - OCFS2 DLM LKSB;
  - requested and blocking levels;
  - wait queue;
  - work item for downconversion.
- `dlmfs_inode_private` embeds:
  - cluster connection pointer;
  - `user_lock_res`;
  - parent inode pointer;
  - VFS inode.
- `dlmfs_filp_private` stores the lock level acquired by a file open.

## Exposed Interfaces
- Lock resource lifecycle:
  - `user_dlm_lock_res_init()`
  - `user_dlm_destroy_lock()`
- Lock operations:
  - `user_dlm_cluster_lock()`
  - `user_dlm_cluster_unlock()`
- LVB access:
  - `user_dlm_write_lvb()`
  - `user_dlm_read_lvb()`
- Domain/protocol operations:
  - `user_dlm_register()`
  - `user_dlm_unregister()`
  - `user_dlm_set_locking_protocol()`

## Coupling
This header is tightly coupled to dlmfs inode layout: `DLMFS_I()` uses `container_of()` to recover `dlmfs_inode_private` from a VFS inode, enabling both VFS code and DLM protocol code to share the same inode-private lock state.
