# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap.c

Implements XFS reverse mapping btree semantic operations. Reverse mappings record physical block ownership by owner and logical offset, supporting metadata ownership, file data, reflink-overlapping mappings, unwritten conversion, deferred rmap intents, realtime rmap support, live hooks, and owner-count queries.

Key responsibilities:
- Lookup, insert, delete, update, and validate rmap records.
- Convert on-disk records to `xfs_rmap_irec`, including packed offset/flag decoding.
- Validate AG rmaps and realtime rmaps with separate rules for metadata and inode owners.
- Map and unmap physical extents, coalescing adjacent records where possible.
- Split existing records when unmapping middle ranges.
- Convert written/unwritten state with extensive case handling for left/right fill and neighbor contiguity.
- Provides shared/reflink-safe variants using delete+insert when key fields may overlap with other owners.
- Implements optimized left-neighbor and overlapping range lookups.
- Provides live rmap update hooks under `CONFIG_XFS_LIVE_HOOKS`.
- Processes deferred rmap intents for AG and realtime groups.
- Schedules rmap updates from bmap operations and metadata allocation/free operations.
- Counts matching and nonmatching owners for a physical range, used by scrub/repair/refcount validation.

Important functions:
- `xfs_rmap_lookup_le`, `xfs_rmap_lookup_eq`, `xfs_rmap_lookup_le_range`
- `xfs_rmap_get_rec`, `xfs_rmap_btrec_to_irec`, `xfs_rmap_check_irec`, `xfs_rtrmap_check_irec`
- `xfs_rmap_map`, `xfs_rmap_unmap`, `xfs_rmap_convert`
- `xfs_rmap_map_shared`, `xfs_rmap_unmap_shared`, `xfs_rmap_convert_shared`
- `xfs_rmap_map_extent`, `xfs_rmap_unmap_extent`, `xfs_rmap_convert_extent`
- `xfs_rmap_alloc_extent`, `xfs_rmap_free_extent`
- `xfs_rmap_finish_one`, `__xfs_rmap_finish_intent`
- `xfs_rmap_query_range`, `xfs_rmap_query_all`
- `xfs_rmap_count_owners`, `xfs_rmap_has_other_keys`
- `xfs_rmap_map_raw`

Design notes:
- Non-inode owners and bmbt blocks ignore logical offsets for merge decisions.
- Reflink data mappings are shareable and can overlap physically, so shared variants avoid unsafe in-place key changes.
- Corruption handling consistently marks the relevant btree sick.
- Deferred intent cursor reuse avoids repeated AGF/rtgroup locking and reduces lock ordering problems.
