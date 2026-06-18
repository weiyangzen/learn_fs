# File Research: sources/local-fs/kdave-linux/fs/btrfs/delalloc-space.c

This file implements Btrfs delayed allocation space accounting for buffered/direct writes, covering both data-space reservations and metadata/qgroup reservations needed for future file extent and checksum items.

Core responsibilities:
- Reserve data bytes against `space_info->bytes_may_use` before dirtying ranges.
- Free data reservations on error or unused ranges.
- Reserve per-inode metadata in `inode->block_rsv` based on `outstanding_extents` and `csum_bytes`.
- Coordinate qgroup data and metadata prealloc reservations.
- Maintain the temporary `outstanding_extents` accounting lifecycle around delalloc, ordered extents, and completion.

Key mechanisms:
- `data_sinfo_for_inode()` selects normal data space info, except zoned data relocation uses the relocation data subgroup.
- `btrfs_alloc_data_chunk_ondemand()` aligns bytes to sectorsize and reserves data bytes, using the free-space-inode flush policy when needed.
- `btrfs_check_data_free_space()` reserves data bytes first, then qgroup data range reservation; failure unwinds both.
- `btrfs_free_reserved_data_space_noquota()` only frees `bytes_may_use`, for contexts that cannot use accurate qgroup reservation handling.
- `btrfs_free_reserved_data_space()` aligns the range, frees data bytes, and releases qgroup data reservation records.
- `btrfs_calculate_inode_block_rsv_size()` recalculates the inode block reserve size from `outstanding_extents`, inode update metadata, checksum leaves, and qgroup metadata estimate.
- `calc_inode_reservations()` computes an upfront reservation for a new write operation, intentionally over-reserving rather than letting many inodes accumulate partial reservations.
- `btrfs_delalloc_reserve_metadata()` reserves qgroup metadata and metadata bytes, then updates `outstanding_extents` and `csum_bytes` before adding bytes to `inode->block_rsv`.
- `btrfs_delalloc_release_metadata()` subtracts checksum bytes, recalculates the reservation, and releases excess block reserve space.
- `btrfs_delalloc_release_extents()` drops the temporary outstanding extent count that was held during reservation.
- `btrfs_delalloc_shrink_extents()` adjusts outstanding extent count when a previously reserved range shrinks.
- `btrfs_delalloc_reserve_space()` combines data and metadata reservation for delalloc.
- `btrfs_delalloc_release_space()` releases metadata and data reservation together.

Important invariants:
- Ranges are sectorsize aligned before reservation/free.
- Metadata accounting updates `inode->outstanding_extents` and `inode->csum_bytes` under `inode->lock`.
- `btrfs_delalloc_reserve_metadata()` must be paired with `btrfs_delalloc_release_extents()` once the caller’s temporary reservation responsibility has moved to delalloc or ordered extent state.
- `qgroup_free` distinguishes error cleanup from normal conversion into transaction-scoped qgroup metadata accounting.

Cross-file relationships:
- Used by direct I/O write setup in `direct-io.c`.
- Depends on block reserve helpers from `block-rsv.h`, space reservation from `space-info.h`, qgroup APIs from `qgroup.h`, and inode accounting from `btrfs_inode.h`.
