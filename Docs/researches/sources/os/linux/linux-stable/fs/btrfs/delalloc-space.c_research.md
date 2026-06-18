# File Research: sources/os/linux/linux-stable/fs/btrfs/delalloc-space.c

This file implements Btrfs delayed allocation data and metadata space accounting. It is the reservation layer used before dirty buffered data, direct I/O allocations, ordered extents, checksum items, and extent-tree updates become fully committed filesystem metadata.

Key responsibilities:
- Reserve and release data bytes in `space_info->bytes_may_use`.
- Reserve and release qgroup data and metadata space.
- Maintain per-inode delayed allocation metadata reserve state through `inode->block_rsv`.
- Track `inode->outstanding_extents` and `inode->csum_bytes`.
- Convert reservation ownership between prealloc/qgroup metadata accounting and transaction accounting.
- Handle zoned data relocation using a special data-relocation subgroup.

Important functions:
- `data_sinfo_for_inode()` selects normal data space info, except zoned data relocation roots use `BTRFS_SUB_GROUP_DATA_RELOC`.
- `btrfs_alloc_data_chunk_ondemand()` aligns requested bytes and reserves data bytes with the correct flush mode.
- `btrfs_check_data_free_space()` reserves data bytes and qgroup data ranges, rolling back both on failure.
- `btrfs_free_reserved_data_space_noquota()` drops data bytes from `bytes_may_use` without qgroup handling.
- `btrfs_free_reserved_data_space()` aligns the range, frees data reservation, and frees qgroup data reservation.
- `btrfs_calculate_inode_block_rsv_size()` recomputes the inode block reserve size from outstanding extents and checksum leaves.
- `calc_inode_reservations()` calculates metadata and qgroup reservation sizes for a new dirty range.
- `btrfs_delalloc_reserve_metadata()` pre-reserves metadata/qgroup space, updates `outstanding_extents` and `csum_bytes`, then adds bytes to the inode block reserve.
- `btrfs_delalloc_release_metadata()` subtracts checksum bytes, recalculates the reserve, and releases excess metadata.
- `btrfs_delalloc_release_extents()` releases the temporary outstanding-extents accounting taken during reservation.
- `btrfs_delalloc_shrink_extents()` adjusts outstanding extent count when a previously reserved range shrinks.
- `btrfs_delalloc_reserve_space()` combines data and metadata reservation for delayed allocation.
- `btrfs_delalloc_release_space()` releases both metadata and data reservations.

Concurrency and invariants:
- `inode->lock` protects `outstanding_extents`, `csum_bytes`, and block reserve size recalculation.
- `block_rsv->lock` protects block reserve size and qgroup reservation fields.
- Reservation order is deliberate: qgroup metadata, metadata bytes, inode counters, then block reserve bytes.
- `btrfs_is_testing()` bypasses actual block reserve release in test contexts.
- All data reservation lengths are sectorsize-aligned.

Error handling:
- Data reservation failure returns immediately.
- Qgroup data reservation failure frees data bytes and the extent changeset.
- Metadata reservation failure frees qgroup prealloc.
- Combined reservation failure frees data/qgroup reservations and resets the caller changeset pointer.

Role in Btrfs:
This file is central to ENOSPC correctness for delayed allocation. It bridges user writes, qgroup limits, ordered extents, checksums, and metadata insertion costs before actual extent and checksum items are written.
