# File Research: sources/local-fs/jfsutils/libfs/diskmap.h

## Purpose
Declares the userspace JFS disk allocation map helper API used to construct and validate dmap buddy trees and allocation-group sizing.

## Interface
- `ujfs_maxbuddy(unsigned char *)`: computes maximum buddy/free-run state for a bitmap word or byte sequence.
- `ujfs_adjtree(int8_t *, int32_t, int32_t)`: adjusts/rebuilds a fixed-size summary tree.
- `ujfs_complete_dmap(struct dmap *, int64_t, int8_t *)`: completes a dmap page from allocation bitmap state.
- `ujfs_idmap_page(struct dmap *, uint32_t)`: initializes/identifies a dmap page.
- `ujfs_getagl2size(int64_t, int32_t)`: computes allocation-group log2 size from aggregate size/block size context.

## Dependencies
Includes `jfs_types.h` for fixed-width types and forward-declares `struct dmap`; concrete layout comes from `jfs_dmap.h` in callers/implementations.

## Notes
This is a narrow header with no state. It forms the public boundary for `diskmap.c` and overlaps conceptually with the local buddy-tree rebuild logic in `log_map.c`.
