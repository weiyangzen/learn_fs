# File Research: sources/os/linux/linux/fs/btrfs/delalloc-space.c

This file implements Btrfs delayed allocation reservation accounting for data writes. It coordinates the data space reservation made before dirtying a range with the metadata and qgroup reservations needed later for file extent items, inode updates, and checksum items.

Core responsibilities:
- Reserve and release data bytes in the correct `btrfs_space_info`, including a zoned data-relocation subgroup special case.
- Keep qgroup data reservations synchronized with data-space reservations through `extent_changeset`.
- Maintain per-inode metadata reservations in `inode->block_rsv`.
- Track `inode->outstanding_extents` and `inode->csum_bytes` so the inode block reserve reflects worst-case pending metadata.
- Provide combined delalloc reserve/release helpers used by buffered and direct write paths.

Key mechanisms:
- `data_sinfo_for_inode()` chooses normal data space info unless a zoned data relocation root must use `BTRFS_SUB_GROUP_DATA_RELOC`.
- `btrfs_alloc_data_chunk_ondemand()` aligns bytes to sectorsize and reserves data bytes with a normal data flush policy or the free-space-inode policy.
- `btrfs_check_data_free_space()` aligns the requested range, reserves data bytes, then reserves qgroup data; qgroup failure unwinds data reservation and frees the changeset.
- `btrfs_free_reserved_data_space_noquota()` releases only data `bytes_may_use`, for contexts where accurate qgroup reservation handling is inappropriate.
- `btrfs_free_reserved_data_space()` aligns the range, frees data reservation, and frees qgroup data reservation.
- `btrfs_calculate_inode_block_rsv_size()` recalculates the per-inode block reserve from outstanding extent count, one inode update, and checksum leaves unless `NODATASUM` is set.
- `calc_inode_reservations()` computes an upfront metadata and qgroup reservation for a write operation using `count_max_extents()` and checksum leaf estimates.
- `btrfs_delalloc_reserve_metadata()` performs qgroup metadata prealloc, reserves metadata bytes, updates inode counters under `inode->lock`, then adds bytes to the inode block reserve.
- `btrfs_delalloc_release_metadata()`, `btrfs_delalloc_release_extents()`, and `btrfs_delalloc_shrink_extents()` rebalance the counters and release excess reservations.
- `btrfs_delalloc_reserve_space()` and `btrfs_delalloc_release_space()` combine the data and metadata sides.

Important invariants:
- Reservation and release lengths are sectorsize aligned.
- Temporary outstanding extent reservations made by `btrfs_delalloc_reserve_metadata()` must later be released with `btrfs_delalloc_release_extents()` once delalloc or ordered extent accounting owns the range.
- `qgroup_free` selects whether metadata qgroup prealloc is freed as an error path or converted into transaction-scoped accounting for normal completion.
- Testing mode skips actual block reservation release in several metadata release helpers.

Cross-file relationships:
- Direct I/O write setup in `direct-io.c` calls these helpers when it needs COW, NOCOW, or prealloc ordered extents.
- The API is declared by `delalloc-space.h`.
- Reservation primitives come from block reserve, space info, qgroup, inode, and filesystem helpers.
