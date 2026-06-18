# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rmap.c

Implements reverse mapping record operations for XFS rmap btrees. It tracks physical extent ownership by owner, fork, offset, and flags; supports shared reflink-aware overlapping records; processes deferred rmap intents; exposes query/count helpers; and validates both AG and realtime rmap records.

Core record operations:
- `xfs_rmap_lookup_le` and `xfs_rmap_lookup_eq` search by physical block, owner, offset, and flags.
- `xfs_rmap_insert`, internal `xfs_rmap_delete`, and `xfs_rmap_update` mutate btree records.
- `xfs_rmap_btrec_to_irec` unpacks on-disk records, including offset flags.
- `xfs_rmap_check_irec` validates AG rmap records, including owner class, AG header special cases, file offsets, bmbt/attr/unwritten rules, and extent bounds.
- `xfs_rtrmap_check_irec` applies realtime-specific rules, allowing realtime filesystem metadata, CoW metadata when realtime reflink is enabled, and inode-owned data extents.

Mapping and unmapping:
- `xfs_rmap_map` handles non-overlapping rmap insertion and merges adjacent compatible records.
- `xfs_rmap_unmap` removes or splits records for freed/unmapped extents, with special handling for growfs null-owner extents and unknown-owner EFI recovery.
- `xfs_rmap_map_shared` and `xfs_rmap_unmap_shared` are overlap-aware variants for reflink file data; they use delete/insert when key fields change because neighboring records may belong to other owners.
- `xfs_rmap_map_raw` inserts a raw rmap, choosing shared or non-shared logic based on flags and owner class.

Conversion logic:
- `xfs_rmap_convert` toggles unwritten state for non-overlapping mappings.
- `xfs_rmap_convert_shared` performs the same operation for possibly overlapping reflink data records.
- Both conversion paths compute left/right adjacency and filling state, then update/delete/insert records to preserve btree order and maximize coalescing.

Deferred intents:
- `xfs_rmap_finish_one` processes deferred map, unmap, convert, alloc, and free operations, reusing a cursor while intents remain in the same group.
- `xfs_rmap_finish_init_cursor` refreshes AG freelist state before rmapbt updates.
- `xfs_rtrmap_finish_init_cursor` locks and joins realtime rmap state.
- Public enqueue helpers include `xfs_rmap_map_extent`, `xfs_rmap_unmap_extent`, `xfs_rmap_convert_extent`, `xfs_rmap_alloc_extent`, and `xfs_rmap_free_extent`.

Query and ownership analysis:
- `xfs_rmap_query_range` and `xfs_rmap_query_all` validate and pass rmap records to callbacks.
- `xfs_rmap_has_records` checks physical keyspace coverage.
- `xfs_rmap_count_owners` counts matching and nonmatching owners over a range.
- `xfs_rmap_has_other_keys` stops early when another owner overlaps the queried range.
- Shareability checks distinguish reflink-shareable file data from metadata or bmbt/attr records.

Live hook support:
- Under `CONFIG_XFS_LIVE_HOOKS`, rmap updates can notify registered hooks through a static switch.
- Hook APIs allow online fsck or similar users to monitor rmap updates with low inactive overhead.

Important interactions:
- Uses `xfs_rmap_btree.c` for AG rmapbt cursor/geometry.
- Uses realtime rmap btree support for rtgroup-backed records.
- Receives owner information from allocation, inode bmap, refcount CoW staging, and metadata allocation paths.
- Exposes owner constants such as `XFS_RMAP_OINFO_REFC`, `XFS_RMAP_OINFO_COW`, and `XFS_RMAP_OINFO_ANY_OWNER`.

Risk points:
- Offset flags are part key and part attribute: unwritten is ignored for key ordering, while attr fork and bmbt flags are key-significant.
- Shared rmap updates must not rely on adjacent cursor records belonging to the same owner.
- Unknown-owner recovery paths intentionally relax owner checks but still enforce range consistency.
