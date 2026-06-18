# File Research: sources/os/linux/linux-stable/fs/ocfs2/sysfile.c

Implements lookup and caching of OCFS2 system file inodes.

Key behavior:
- `ocfs2_get_system_file_inode()` returns an inode reference for a global or slot-local system file.
- Global system inodes are cached in `osb->global_system_inodes[type]`.
- Local system inodes are cached in a lazily allocated `NUM_LOCAL_SYSTEM_INODES * max_slots` array.
- `system_file_mutex` serializes cache lookup/population and protects the extra cached inode reference.
- `_ocfs2_get_system_file_inode()` formats the system inode name, looks it up under `osb->sys_root_inode`, and loads it with `ocfs2_iget(..., OCFS2_FI_FLAG_SYSFILE, type)`.
- Under `CONFIG_DEBUG_LOCK_ALLOC`, lockdep classes are assigned per system inode type, with journal and local quota inodes exempted because their cluster locks are not process-owned in a lockdep-friendly way.

Integration points:
- Mount code loads root/system/global/local system inodes through this file.
- Allocator, quota, journal, truncate log, local alloc, bitmap, and recovery paths retrieve their system files here.

Concurrency and lifetime:
- Cached arrays hold one persistent inode reference; callers receive an additional `igrab()` reference.
- Local system inode array allocation is race-tolerant: if another thread installs the array first, the loser frees its allocation.

Risk areas:
- System inode name formatting and lookup must match on-disk system directory entries.
- Missing system files usually indicate corruption or unsupported feature state.
- Cached references must be released by `ocfs2_release_system_inodes()` during dismount and mount failure cleanup.
