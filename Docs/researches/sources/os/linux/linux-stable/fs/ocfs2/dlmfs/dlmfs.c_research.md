# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlmfs/dlmfs.c

## Purpose

Implements `ocfs2_dlmfs`, a small pseudo filesystem exposing OCFS2 DLM locks to userspace through filesystem operations. Directories represent DLM domains, regular files represent locks, opening files acquires locks, closing files releases locks, and reading/writing files accesses the lock value block.

## Major Responsibilities

- Register the `ocfs2_dlmfs` filesystem.
- Allocate/free private dlmfs inodes.
- Create DLM domains via root-level directories.
- Create DLM lock resources via files inside domain directories.
- Acquire cluster locks on file open.
- Release cluster locks on file close.
- Expose BAST notifications through `poll()`.
- Expose LVB contents through read/write.
- Register/unregister per-domain cluster connections.
- Manage module init/exit resources.

## ABI Capabilities

The file exposes read-only module parameter `capabilities`.

Current capability string:

- `bast`
- `stackglue`

The comments explain that this exists because some ABI features, such as meaningful poll behavior, are not discoverable by normal use.

## Filesystem Model

- Filesystem type name: `ocfs2_dlmfs`
- Magic: `DLMFS_MAGIC`
- Root inode is a directory.
- Only root supports `mkdir`.
- Domain directories support:
  - file create
  - lookup
  - unlink
- Regular files support:
  - open
  - release
  - poll
  - read
  - write
  - llseek
  - getattr
  - setattr with size changes ignored

Nested directories are not supported by the operation table; only top-level domain directories can be created.

## Open/Close Locking

`dlmfs_decode_open_flags()` maps open flags to lock semantics:

- `O_WRONLY` or `O_RDWR`: exclusive lock
- otherwise: protected/read lock
- `O_NONBLOCK`: noqueue flag

`dlmfs_file_open()`:

1. Rejects directory opens through BUG path.
2. Decodes flags.
3. Clears `O_APPEND` because append has no meaning for fixed-size LVB writes.
4. Allocates `dlmfs_filp_private`.
5. Calls `user_dlm_cluster_lock()`.
6. Maps noqueue `-EAGAIN` to `-ETXTBSY` so userspace can distinguish “not granted”.
7. Stores the acquired lock level in file private data.

`dlmfs_file_release()`:

- Reads the lock level from private data.
- Calls `user_dlm_cluster_unlock()` unless level is IV.
- Frees private data.

## LVB Read/Write

`dlmfs_file_read()`:

- Calls `user_dlm_read_lvb()`.
- Returns 0 if the LVB is invalid.
- Otherwise returns from a fixed `DLM_LVB_LEN` buffer.

`dlmfs_file_write()`:

- Bounds writes to `DLM_LVB_LEN`.
- Returns `-ENOSPC` if offset is already past the LVB.
- Copies from userspace into a stack buffer.
- Calls `user_dlm_write_lvb()` if any bytes were copied.
- Advances file offset.

The inode size is set to `DLM_LVB_LEN` for regular lock files.

## Poll

`dlmfs_file_poll()` waits on `ip_lockres.l_event`.

It returns readable events when `USER_LOCK_BLOCKED` is set, allowing userspace to observe that a BAST fired and the held lock is blocking another node.

## Inode Lifecycle

`dlmfs_inode_private` embeds a VFS inode plus:

- cluster connection pointer
- user lock resource
- parent inode pointer

`dlmfs_alloc_inode()` allocates from `dlmfs_inode_cache`.

`dlmfs_evict_inode()`:

- For regular files:
  - destroys the user lock unless already in teardown
  - drops parent inode ref
- For directories:
  - unregisters the cluster connection if present

`dlmfs_get_inode()` initializes regular-file lock resources with `user_dlm_lock_res_init()` and grabs the parent inode so child locks are destroyed before parent domain unregister.

## Domain And Lock Creation

`dlmfs_mkdir()`:

- Only available on root inode.
- Validates domain length against `GROUP_NAME_MAX`.
- Allocates a directory inode.
- Calls `user_dlm_register()` to connect to the cluster domain.
- Stores the returned connection in inode private data.
- Makes the dentry persistent.

`dlmfs_create()`:

- Validates lock name length against `USER_DLM_LOCK_ID_MAX_LEN`.
- Rejects names starting with `$`, reserving internal DLM names.
- Allocates a regular inode and makes the dentry persistent.

`dlmfs_unlink()`:

- Calls `user_dlm_destroy_lock()`.
- Then performs `simple_unlink()`.

## Mount And Module Setup

`dlmfs_fill_super()` configures superblock fields and root dentry.

`init_dlmfs_fs()`:

1. Creates inode cache.
2. Allocates `user_dlm_worker` workqueue.
3. Sets max locking protocol through `user_dlm_set_locking_protocol()`.
4. Registers filesystem.

`exit_dlmfs_fs()`:

1. Unregisters filesystem.
2. Destroys workqueue.
3. Runs `rcu_barrier()`.
4. Destroys inode cache.

## Dependencies

- Linux VFS simple filesystem helpers.
- OCFS2 stackglue.
- `userdlm.c` for actual cluster locking.
- Workqueue exported as `user_dlm_worker`.
- OCFS2 mask logging.

## Research Notes

`dlmfs.c` is the VFS translation layer. It intentionally keeps filesystem behavior minimal and maps common filesystem actions to DLM operations. The actual lock state machine is delegated to `userdlm.c`; this file owns object lifetime, ABI exposure, and safe filesystem integration.
