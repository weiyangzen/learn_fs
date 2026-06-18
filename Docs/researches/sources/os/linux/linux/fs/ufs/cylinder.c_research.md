# File Research: sources/os/linux/linux/fs/ufs/cylinder.c

Purpose: UFS cylinder group cache loading, release, and LRU management.

Key behavior:
- `ufs_read_cylinder()` loads all buffer fragments for a cylinder group into a preallocated `ufs_cg_private_info`, records the group number, and copies important cylinder group fields into CPU-endian cached fields.
- `ufs_put_cylinder()` writes rotor fields back to the on-disk cylinder group, marks buffers dirty, releases secondary buffers, and marks cache slot empty.
- `ufs_load_cylinder()` returns a cached cylinder group or loads it, using direct indexing when group count is small and an LRU list when only `UFS_MAX_GROUP_LOADED` groups are cached.

Integration:
- Used by block and inode allocation/free paths in `balloc.c` and `ialloc.c`.
- Depends on superblock private geometry and `ufs_buffer_head` helpers.

Risks and invariants:
- Invalid cylinder group numbers panic as internal errors.
- Failed reads release already-read buffers and leave the cache slot empty.
- Rotor updates are considered low-importance and are written when a group is evicted.
