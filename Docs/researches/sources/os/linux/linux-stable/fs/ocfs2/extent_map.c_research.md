# File Research: sources/os/linux/linux-stable/fs/ocfs2/extent_map.c

Purpose: Provides OCFS2 logical-to-physical cluster/block mapping, a tiny inode-local extent cache, FIEMAP support, SEEK_DATA/SEEK_HOLE support, overwrite checks, xattr extent lookup, and virtual-block reads.

Read coverage: complete file read, 1047 lines.

Key structures and state:
- Uses `struct ocfs2_extent_map` embedded in `ocfs2_inode_info`, capped at `OCFS2_MAX_EXTENT_MAP_ITEMS` entries.
- `struct ocfs2_extent_map_item` records logical cluster start, physical cluster start, cluster count, flags, and LRU list linkage.
- On-disk mappings are read from dinode extent lists or external extent blocks.

Major logic:
- Initializes, looks up, truncates, inserts, merges, and evicts cached extent-map records under `ip_lock`.
- `ocfs2_get_clusters_nocache()` walks the dinode/extent-block tree, returns the matching extent record or computes hole length, and can identify the last extent.
- `ocfs2_get_clusters()` first consults the small cache, then rereads the dinode and caches successful extent records.
- `ocfs2_extent_map_get_blocks()` converts virtual block numbers to physical block numbers and contiguous block counts.
- `ocfs2_xattr_get_clusters()` maps clusters in an xattr extent list and treats holes in xattr storage as corruption.
- `ocfs2_fiemap()` reports inline data/fast symlinks or extent records, including unwritten and shared/refcounted flags.
- `ocfs2_overwrite_io()` verifies a nowait write range is fully allocated and not refcounted.
- `ocfs2_seek_data_hole_offset()` implements SEEK_DATA/SEEK_HOLE semantics, treating unwritten extents as holes.
- `ocfs2_read_virt_blocks()` maps virtual blocks and reads their physical blocks, supporting readahead validation paths.

Important entry points:
- Cache management: `ocfs2_extent_map_init()`, `ocfs2_extent_map_trunc()`, `ocfs2_extent_map_insert_rec()`.
- Mapping: `ocfs2_get_clusters()`, `ocfs2_xattr_get_clusters()`, `ocfs2_extent_map_get_blocks()`, `ocfs2_figure_hole_clusters()`.
- Reporting and policy checks: `ocfs2_fiemap()`, `ocfs2_overwrite_io()`, `ocfs2_seek_data_hole_offset()`.
- I/O helper: `ocfs2_read_virt_blocks()`.

Concurrency and lifetime:
- Cache list state is protected by `ip_lock`.
- Mapping callers are expected to hold `ip_alloc_sem` when allocations must not change during lookup.
- FIEMAP drops and reacquires `ip_alloc_sem` around `fiemap_fill_next_extent()` to avoid page-fault deadlocks.
- Virtual block reads use `down_read_trylock()` on `ip_alloc_sem`; failure returns `-EAGAIN`.

Important dependencies:
- Relies on extent tree traversal helpers from allocation code, inode block reading, metadata cache validation, OCFS2 block/cluster conversion helpers, FIEMAP, buffer-head I/O, and inline-data/fast-symlink helpers.

Risk and edge cases:
- The extent cache is deliberately small and simple; callers must truncate it whenever records are deleted or mappings can overlap stale entries.
- Corrupt extent-list metadata, non-leaf blocks where leaves are expected, invalid `l_next_free_rec`, or zero physical block records produce filesystem errors.
- Hole length can span to `UINT_MAX - v_cluster`, so callers must cap returned ranges to their own request.
- Inline-data files are not valid for normal cluster lookup and return `-ERANGE`.
