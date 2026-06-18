# File Research: sources/os/linux/linux/fs/ocfs2/extent_map.c

OCFS2 in-memory extent cache and logical-to-physical mapping implementation. It provides a small inode-local extent map, on-disk extent tree lookup helpers, fiemap support, overwrite detection, SEEK_DATA/SEEK_HOLE handling, xattr extent mapping, and virtual block reads.

Extent cache:
- The cache is intentionally tiny: `OCFS2_MAX_EXTENT_MAP_ITEMS` is 3.
- `ocfs2_extent_map_init()` initializes per-inode list state.
- `ocfs2_extent_map_lookup()` searches the list under `ip_lock`, returns physical cluster/length/flags, and moves hits to the front.
- `ocfs2_extent_map_trunc()` forgets all cached mappings at or beyond a logical cluster and trims overlapping cached records.
- `ocfs2_extent_map_insert_rec()` inserts or merges a disk extent record into the cache. It merges adjacent records with identical flags and overwrites overlapping mappings caused by rare flag-split cases.
- When full, the oldest list entry is reused.

On-disk extent lookup:
- `ocfs2_get_clusters_nocache()` reads the dinode extent list or descends to the leaf extent block with `ocfs2_find_leaf()`.
- It validates leaf depth, `l_next_free_rec <= l_count`, nonzero physical block numbers, and can report whether a found record is the last extent.
- Holes are reported through `hole_len` using `ocfs2_figure_hole_clusters()`.
- `ocfs2_last_eb_is_empty()` handles the special case where the rightmost leaf exists but is empty.
- `ocfs2_xattr_get_clusters()` performs similar mapping for xattr extent lists.

Public mapping:
- `ocfs2_get_clusters()` first consults the small cache, then reads the dinode and walks extents. It returns `p_cluster == 0` for holes and inserts found records into the cache.
- Inline-data files return `-ERANGE` from `ocfs2_get_clusters()`.
- `ocfs2_extent_map_get_blocks()` maps logical file blocks to physical blocks and block counts, preserving holes as physical block zero.
- Callers are expected to hold `ip_alloc_sem` where allocation stability matters.

Fiemap:
- `ocfs2_fiemap()` takes the inode metadata lock and `ip_alloc_sem`.
- Inline-data files and fast symlinks are handled by `ocfs2_fiemap_inline()`, which reports the dinode-resident byte range as inline data.
- Extent-backed files are walked without cache, skipping holes and reporting unwritten and shared/refcounted flags.
- The code releases `ip_alloc_sem` around `fiemap_fill_next_extent()` to avoid page-fault deadlocks.

Overwrite and seek helpers:
- `ocfs2_overwrite_io()` returns success only when a write range is fully backed by allocated, non-refcounted extents; otherwise `-EAGAIN`.
- `ocfs2_seek_data_hole_offset()` implements SEEK_DATA and SEEK_HOLE over extents. Unwritten extents count as holes. Inline-data files have data until EOF and hole at EOF.

Virtual block reads:
- `ocfs2_read_virt_blocks()` maps logical file blocks through the extent map and then calls `ocfs2_read_blocks()`.
- It rejects holes as I/O errors for callers that expect metadata-like allocated virtual blocks.
- Uses trylock on `ip_alloc_sem` and returns `-EAGAIN` if unavailable.

Important invariants and risks:
- Cache invalidation is explicit; deletion paths must call truncate/invalidation before stale physical mappings can be reused.
- Hole length can exceed maximum single extent length, so holes are carried separately from `ocfs2_extent_rec`.
- Extent tree corruption is escalated through `ocfs2_error()` and `-EROFS`.
- The fiemap and read-virt paths carefully avoid lock/page-fault deadlocks by dropping semaphores or using trylocks.
