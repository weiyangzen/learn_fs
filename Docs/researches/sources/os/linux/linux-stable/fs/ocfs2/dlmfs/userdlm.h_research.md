# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/userdlm.h

## Purpose

Defines the private data structures, flags, constants, and function prototypes shared by `dlmfs.c` and `userdlm.c`.

## Key Constants And Flags

`USER_DLM_LOCK_ID_MAX_LEN` is `32`.

`user_lock_res->l_flags` bits:

- `USER_LOCK_ATTACHED`: DLM lock/LVB initialized.
- `USER_LOCK_BUSY`: lock operation in progress.
- `USER_LOCK_BLOCKED`: blocked and waiting to downconvert.
- `USER_LOCK_IN_TEARDOWN`: lock is being destroyed.
- `USER_LOCK_QUEUED`: lock resource has queued work.
- `USER_LOCK_IN_CANCEL`: cancel operation in progress.

`DLMFS_MAGIC` is `0x76a9f425`.

## Structures

`struct user_lock_res`

Represents one userspace-visible lock file’s DLM state:

- spinlock
- flags
- fixed-size lock name
- current level
- PR and EX holder counts
- OCFS2 DLM LKS block
- requested level
- blocking level
- wait queue
- work item

`struct dlmfs_inode_private`

Embeds the VFS inode and dlmfs-specific state:

- cluster connection pointer
- `user_lock_res` for regular files
- parent inode pointer
- embedded `struct inode`

Directories use the connection pointer; regular files use the lock resource and parent pointer.

`struct dlmfs_filp_private`

Stores the lock level acquired by one open file instance.

## Helper

`DLMFS_I()` converts a VFS inode to `struct dlmfs_inode_private` using `container_of()`.

## Declared API

The header declares:

- lock resource initialization/destruction
- cluster lock/unlock operations
- LVB read/write
- cluster register/unregister
- locking protocol setup
- exported `user_dlm_worker`

## Research Notes

This header captures the dlmfs/userdlm contract. `dlmfs.c` owns VFS object lifetime and calls this API; `userdlm.c` owns the lock protocol state machine behind the structures defined here.
