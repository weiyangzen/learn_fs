# File Research: sources/os/linux/linux/fs/ocfs2/sysfile.c

## Purpose

`sysfile.c` implements lookup and caching for OCFS2 system file inodes. System files include global filesystem metadata files and per-slot local metadata files such as journals, local allocators, and quota files.

## Cache Layout

- Global system inodes are cached in `osb->global_system_inodes[type]`.
- Local system inodes are cached in a lazily allocated flat array:
  - `NUM_LOCAL_SYSTEM_INODES * osb->max_slots`.
  - Index is `(slot * NUM_LOCAL_SYSTEM_INODES) + (type - OCFS2_FIRST_LOCAL_SYSTEM_INODE)`.
- `osb->system_file_mutex` serializes lookup and cache insertion.
- `osb->osb_lock` protects lazy publication of `local_system_inodes`.

## Main Flow

`ocfs2_get_system_file_inode(osb, type, slot)`:

- Chooses the global cache entry or local cache entry based on inode type.
- If a cached inode exists, returns an extra reference from `igrab()`.
- Otherwise calls `_ocfs2_get_system_file_inode()`.
- If a cache slot exists, stores an additional array reference with `igrab()`.

`_ocfs2_get_system_file_inode()`:

- Builds the system inode name using `ocfs2_sprintf_system_inode_name()`.
- Looks up its block number in `osb->sys_root_inode` with `ocfs2_lookup_ino_from_name()`.
- Loads the inode with `ocfs2_iget(..., OCFS2_FI_FLAG_SYSFILE, type)`.
- Under `CONFIG_DEBUG_LOCK_ALLOC`, assigns lockdep classes to system inode cluster locks, while suppressing lockdep for local quota and journal locks that do not belong to a normal process.

## Correctness Notes

- Local system inode cache allocation is opportunistic; if allocation fails, lookup still proceeds without caching.
- The local array publication handles a race where another thread initializes the array first, freeing the loser allocation.
- Cached inode arrays hold their own references; callers always receive an additional reference and must `iput()`.
- The code asserts local inode requests never use `OCFS2_INVALID_SLOT`.
