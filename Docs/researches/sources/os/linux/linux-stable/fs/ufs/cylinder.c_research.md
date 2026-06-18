# File Research: sources/os/linux/linux-stable/fs/ufs/cylinder.c

## Summary
Manages the in-memory cache of UFS cylinder group metadata and bitmaps.

## Main Responsibilities
- Reads a cylinder group into a `ufs_cg_private_info` cache slot.
- Loads all buffer fragments that make up the cylinder group metadata.
- Extracts frequently used cylinder group offsets, rotors, and cluster fields into CPU-native private state.
- Releases cached cylinder groups while writing rotor state back.
- Implements direct indexing for small numbers of cylinder groups and LRU-like rotation for larger filesystems.

## Important Behavior
For filesystems with more than `UFS_MAX_GROUP_LOADED` cylinder groups, cache slot 0 is the most recently used. Loading a miss evicts the least recently used slot.

## Risks
Cylinder group buffers back inode and block bitmaps used by allocation/free paths. Cache slot rotation must preserve the association between `s_cgno[]` and `s_ucpi[]`.
