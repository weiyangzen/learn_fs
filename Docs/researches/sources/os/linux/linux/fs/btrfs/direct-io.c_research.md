# File Research: sources/os/linux/linux/fs/btrfs/direct-io.c

This file implements Btrfs direct I/O using iomap. It bridges iomap callbacks with Btrfs extent maps, ordered extents, data/metadata reservation, NOCOW/prealloc handling, checksum constraints, page-cache invalidation, and completion cleanup.

Core structures:
- `btrfs_dio_data` is per-iomap-iteration state: submitted byte count, qgroup/data reservation changeset, active ordered extent, data-space-reserved flag, and NOCOW completion flag.
- `btrfs_dio_private` extends `btrfs_bio` with file offset and byte count for completion.
- `btrfs_dio_bioset` backs allocation of direct I/O bios.

Range locking and extent preparation:
- `lock_extent_direct()` takes the DIO extent lock before the normal extent lock, rejects or waits on overlapping ordered extents, and prevents stale page-cache interactions. NOWAIT paths return `-EAGAIN` instead of blocking.
- Direct reads avoid waiting on buffered ordered extents in cases that could deadlock with buffered writers.
- `btrfs_create_dio_extent()` creates an extent map when needed and allocates an ordered extent tagged as direct I/O.
- `btrfs_new_extent_direct()` reserves a new COW extent, handles zoned `-EAGAIN` by waiting for zone finish, creates the DIO extent, and frees reserved extents on failure.
- `btrfs_get_blocks_direct_write()` decides between NOCOW, prealloc, and COW. It reserves metadata for NOCOW/prealloc, requires previously reserved data space for COW, creates ordered extents, releases temporary outstanding extent reservations, and updates i_size under the extent lock.

Iomap callbacks:
- `btrfs_dio_iomap_begin()` caps read size for checksum memory, flushes async compressed extents when needed, optionally reserves data space before locking, locks the target range, loads an extent map, and rejects compressed or inline extents to buffered I/O.
- NOWAIT requests avoid multi-extent partial I/O and return `-EAGAIN` where blocking or unsafe short I/O could occur.
- For writes, the begin callback calls `btrfs_get_blocks_direct_write()` and releases unused data reservation for NOCOW or shorter-than-requested COW mappings.
- It translates extent maps into iomap mapped or hole entries and unlocks the correct extent bits.
- `btrfs_dio_iomap_end()` unlocks holes for reads, completes/cancels unwritten write tail ranges, drops ordered extent refs, and frees data reservation changesets.

Bio submission and completion:
- `btrfs_dio_submit_io()` initializes the Btrfs bio, records submitted bytes, splits ordered extents for partial write bios, and submits with `btrfs_submit_bbio()`.
- `btrfs_extract_ordered_extent()` splits extent maps and ordered extents so each submitted write bio has a matching ordered extent, except NOCOW writes do not split the existing extent map.
- `btrfs_dio_end_io()` warns on bio errors, finishes ordered extents for writes, unlocks DIO ranges for reads, restores bio private data, and hands completion back to iomap.

Direct write behavior:
- `btrfs_direct_write()` uses shared inode locking for within-EOF writes when security bits allow it, otherwise exclusive locking.
- True direct write is allowed only for SINGLE or RAID0 data profiles because duplicated profiles could observe changing userspace buffers differently across mirrors.
- Unaligned I/O, checksummed inodes, compressed/inline extents, unsafe NOWAIT cases, or other fallback triggers use buffered I/O.
- For direct writes, the iov iterator is marked nofault and retried after explicit fault-in to avoid deadlocks when writing from mmaped ranges of the same file.
- Buffered fallback writes data, forces and waits writeback for the written range, advances `ki_pos`, and invalidates page cache so subsequent direct reads see persisted data.

Direct read behavior:
- `btrfs_direct_read()` returns 0 when fsverity is active or direct read validation fails, allowing higher layers to use buffered read behavior.
- `check_direct_read()` enforces sectorsize alignment and rejects duplicate iovec base pointers.
- Reads use shared inode locking, disable page faults, set iterator nofault, retry after fault-in when progress is made, and avoid long retry loops by returning accumulated read bytes when progress stalls.

Lifecycle:
- `btrfs_init_dio()` initializes the bioset with space for embedded `btrfs_dio_private`.
- `btrfs_destroy_dio()` exits the bioset.
