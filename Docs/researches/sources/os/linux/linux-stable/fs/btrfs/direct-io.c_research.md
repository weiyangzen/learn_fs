# File Research: sources/os/linux/linux-stable/fs/btrfs/direct-io.c

This file implements Btrfs direct I/O using iomap. It handles direct read/write mapping, extent locking, ordered extents, NOCOW/prealloc writes, COW allocation, fallback to buffered I/O, bio submission, and completion.

Private structures:
- `struct btrfs_dio_data`
  - Tracks submitted byte count, data reservation changeset, current ordered extent, whether data space was reserved, and whether NOCOW succeeded.
- `struct btrfs_dio_private`
  - Stores file offset and byte count for a bio, followed by embedded `struct btrfs_bio`.
- `btrfs_dio_bioset`
  - Bioset used for direct I/O bios.

Range locking:
- `lock_extent_direct()` takes the DIO extent lock before the regular extent lock.
- It waits for conflicting ordered extents and rejects or falls back if page cache invalidation cannot be guaranteed.
- NOWAIT paths return `-EAGAIN` instead of blocking.
- DIO reads avoid waiting for buffered ordered extents in cases that could deadlock.

Direct extent creation:
- `btrfs_create_dio_extent()` creates an extent map when needed and allocates an ordered extent marked direct.
- `btrfs_new_extent_direct()` reserves a new on-disk extent for COW direct writes, retrying zoned allocation after zone finish events.

Direct write block mapping:
- `btrfs_get_blocks_direct_write()` decides between NOCOW/prealloc and COW:
  - NOCOW/prealloc path reserves metadata only, creates ordered extent, and marks `nocow_done`.
  - COW path requires data space reserved before locking, reserves metadata, allocates a new extent, and releases excess metadata if allocation is shorter than requested.
- It releases temporary outstanding extent reservations after ordered extent creation.
- It updates `i_size` under the extent lock for extending writes.

Iomap begin/end:
- `btrfs_dio_iomap_begin()`:
  - Handles NOWAIT restrictions.
  - Caps read length for checksum array sizing.
  - Flushes async compressed pages when needed.
  - Pre-reserves data space for blocking writes before range locking.
  - Locks the DIO/extent range.
  - Looks up extent maps.
  - Falls back for inline or compressed extents.
  - Avoids partial NOWAIT I/O over multiple extents.
  - Performs write-specific mapping/allocation.
  - Fills `struct iomap`.
  - Releases extent locks appropriately while keeping read DIO locks until completion.
- `btrfs_dio_iomap_end()`:
  - Unlocks holes for reads.
  - Handles short submission by finishing/canceling unwritten ordered write ranges or unlocking unread ranges.
  - Drops ordered extent refs and frees data reservation changesets.

Bio completion/submission:
- `btrfs_dio_end_io()` logs bio errors, finishes ordered extents for writes, unlocks DIO extents for reads, restores bio private pointer, and completes iomap bio.
- `btrfs_extract_ordered_extent()` splits ordered extents for partial submitted writes and splits extent maps for non-NOCOW writes.
- `btrfs_dio_submit_io()` initializes `btrfs_bio`, records range, updates submitted bytes, extracts/splits ordered extent for writes, and submits via `btrfs_submit_bbio()`.

Read/write wrappers:
- `btrfs_dio_read()` calls `iomap_dio_rw()` with partial and fsblock-aligned flags.
- `btrfs_dio_write()` calls `__iomap_dio_rw()` with the same direct-I/O flags.

Alignment validation:
- `check_direct_IO()` requires file offset and iterator alignment to sectorsize.
- `check_direct_read()` also rejects duplicate iovec base addresses for direct reads.

Direct write policy:
- `btrfs_direct_write()`:
  - Uses NOWAIT try-locking when requested.
  - Uses shared inode locking only for within-EOF writes that cannot drop security bits.
  - Falls back to buffered writes for duplicated data profiles other than RAID0/SINGLE, because user buffers can change during mirror writes.
  - Falls back to buffered writes if alignment fails or data checksums are enabled.
  - Disables iov page faults during DIO to avoid mmap self-deadlocks, then faults pages and retries on `-EFAULT`.
  - For fallback buffered writes, writes data, flushes/waits it, advances position, and invalidates page cache so subsequent direct reads see persisted data.

Direct read policy:
- `btrfs_direct_read()`:
  - Returns 0 when fsverity is active or direct-read checks fail.
  - Takes shared inode lock.
  - Disables page faults and iov faults during DIO to avoid extent-lock deadlocks.
  - Faults destination pages and retries on partial progress or `-EFAULT`.
  - Returns accumulated bytes read.

Initialization:
- `btrfs_init_dio()` initializes the DIO bioset.
- `btrfs_destroy_dio()` exits the bioset.

Role in Btrfs:
This file is the bridge between Linux iomap direct I/O and Btrfs COW semantics. Its main complexity is preventing stale reads and deadlocks while preserving Btrfs ordered extent, checksum, NOCOW, page-cache, and reservation invariants.
