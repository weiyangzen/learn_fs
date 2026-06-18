# File Research: sources/os/linux/linux/fs/ocfs2/dlmfs/dlmfs.c

## Purpose
Implements `ocfs2_dlmfs`, a small virtual filesystem that exposes OCFS2 DLM locks to userspace. Directories represent DLM domains; regular files represent lock resources.

## Major Responsibilities
- Registers the `ocfs2_dlmfs` filesystem type.
- Creates and destroys a slab cache for dlmfs inode-private data.
- Creates and destroys the `user_dlm` workqueue.
- Exposes read-only ABI capabilities via module parameter `capabilities`, currently `"bast stackglue"`.
- Implements VFS operations for root directories, domain directories, and lock files.
- Bridges file open/close/read/write/poll to `userdlm.c`.

## Filesystem Model
- Root supports `mkdir` only for creating DLM domains.
- Domain directories support regular-file create/unlink and lookup.
- Regular files are lock resources.
- Opening a lock file acquires a DLM lock:
  - `O_RDONLY` maps to PR.
  - `O_WRONLY` or `O_RDWR` maps to EX.
  - `O_NONBLOCK` maps to DLM no-queue behavior.
- Closing the file drops the corresponding holder count.
- File size is fixed to `DLM_LVB_LEN`; setattr ignores requested size changes.

## Key Operations
- `dlmfs_mkdir()` validates domain name length, allocates a directory inode, and calls `user_dlm_register()`.
- `dlmfs_create()` validates lock names, rejects names beginning with `$`, allocates a regular inode, and initializes `user_lock_res`.
- `dlmfs_file_open()` decodes flags, allocates per-file private data, and calls `user_dlm_cluster_lock()`.
- `dlmfs_file_release()` calls `user_dlm_cluster_unlock()`.
- `dlmfs_file_read()` reads the lock value block through `user_dlm_read_lvb()`.
- `dlmfs_file_write()` writes bounded LVB data through `user_dlm_write_lvb()`.
- `dlmfs_file_poll()` reports readable events when a BAST has marked the lock blocked.
- `dlmfs_unlink()` destroys the user lock before unlinking.

## Lifetime Management
- `dlmfs_inode_private` embeds the VFS inode, cluster connection pointer, parent inode pointer, and lock resource.
- Regular-file inodes hold a parent reference so lock teardown occurs before domain unregister.
- Directory eviction unregisters the cluster connection.
- Regular-file eviction destroys the DLM lock unless already in teardown.
- `drop_inode = inode_just_drop` matches the virtual filesystem behavior.

## Concurrency and Error Handling
- Uses `GFP_NOFS` for allocations in filesystem paths.
- Teardown carefully avoids double-destroy using `USER_LOCK_IN_TEARDOWN`.
- Nonblocking lock acquisition maps `-EAGAIN` to `-ETXTBSY` so userspace can distinguish no-queue denial from invalid open.
