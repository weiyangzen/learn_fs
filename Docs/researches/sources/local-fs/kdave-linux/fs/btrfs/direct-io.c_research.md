# File Research: sources/local-fs/kdave-linux/fs/btrfs/direct-io.c

This file implements Btrfs direct I/O on top of iomap. It handles extent locking, DIO mapping, COW/NOCOW decisions, ordered extents, direct bio submission, fallback to buffered I/O, and bioset lifecycle.

Private state:
- `struct btrfs_dio_data`
  - Tracks submitted bytes, qgroup/data reservation changeset, current ordered extent, whether data space was reserved, and whether NOCOW succeeded.
- `struct btrfs_dio_private`
  - Stores file offset/byte count for the bio and embeds `struct btrfs_bio`.
- `btrfs_dio_bioset`
  - Bioset used by iomap direct I/O.

Extent locking:
- `lock_extent_direct()` takes the direct I/O extent lock before the normal extent lock.
- It rejects NOWAIT if either lock would block.
- It checks for ordered extents and, for writes, pagecache pages in the range.
- For blocking DIO writes or DIO ordered extents it waits on ordered extents.
- It returns `-ENOTBLK` to force buffered fallback when it cannot safely proceed without deadlock.
- Reads avoid waiting on buffered ordered extents in some multi-extent cases to prevent page-lock deadlocks.

Direct write extent setup:
- `btrfs_create_dio_extent()` creates an extent map when needed and allocates a direct ordered extent.
- `btrfs_new_extent_direct()` reserves a new extent for COW writes, handling zoned `-EAGAIN` by waiting for zone finish, then creates the DIO extent.
- `btrfs_get_blocks_direct_write()` decides between:
  - NOCOW for suitable existing extents.
  - PREALLOC ordered extent for preallocated extents.
  - COW allocation for everything else.
- NOCOW/PREALLOC reserve metadata only.
- COW requires prior data-space reservation, then metadata reservation and new extent allocation.
- It releases temporary outstanding extent reservation after ordered extent creation.
- It updates `i_size` under extent lock for extending writes.

Iomap begin:
- `btrfs_dio_iomap_begin()`:
  - Rejects large NOWAIT reads that could produce bad short-read behavior.
  - Caps read mapping length to checksum-array-friendly size.
  - Flushes compressed async extents when required.
  - Pre-reserves data space for blocking writes before locking the file range.
  - Locks direct and normal extent state.
  - Gets an extent map.
  - Falls back to buffered I/O for compressed or inline extents.
  - Rejects NOWAIT multi-extent ranges to avoid partial success surprises.
  - For writes, calls `btrfs_get_blocks_direct_write()`.
  - Translates extent map to iomap mapped/hole state.
  - Unlocks normal extent state before returning, while read DIO keeps the DIO lock until I/O completion.
  - Frees unused pre-reserved data space for short mappings or NOCOW.

Iomap end:
- `btrfs_dio_iomap_end()` unlocks holes for reads.
- If less was submitted than mapped, it finishes the unwritten part of write ordered extent as failed or unlocks read DIO extent, then returns `-ENOTBLK`.
- For writes it drops the ordered extent and frees the data reservation changeset.

Bio completion and submission:
- `btrfs_dio_end_io()` logs failed direct I/O, finishes write ordered extents on write completion, unlocks DIO extents on read completion, restores bio private data, then calls iomap completion.
- `btrfs_extract_ordered_extent()` splits ordered extents and extent maps for partial submitted writes; NOCOW skips extent map splitting.
- `btrfs_dio_submit_io()` initializes `btrfs_bio`, records submitted byte count, extracts/splits ordered extents for writes, and submits through `btrfs_submit_bbio()`.

Direct write entry:
- `btrfs_direct_write()`:
  - Uses NOWAIT try-locking when requested.
  - Uses shared inode lock for within-EOF writes when security bits do not need removal.
  - Falls back to buffered I/O for duplicated data profiles other than RAID0/SINGLE, because user buffers could mutate and diverge across mirrors/parity.
  - Runs generic write checks and Btrfs write checks.
  - Requires sectorsize-aligned offset and iov alignment.
  - Falls back to buffered I/O when data checksums are enabled, because user memory can change after checksum calculation.
  - Disables iov faults around iomap DIO to avoid self-deadlocks when the input buffer maps the same file range.
  - Retries after faulting in remaining pages; if no progress is made, falls back to buffered.
  - Buffered fallback writes, flushes and waits the written range, updates position, and invalidates pagecache so later DIO reads see persisted data.
  - NOWAIT buffered fallback returns `-EAGAIN`.

Direct read entry:
- `check_direct_read()` requires sectorsize alignment and rejects duplicate iovec base addresses.
- `btrfs_direct_read()` returns 0 if fsverity is active or checks fail, causing normal buffered handling by callers.
- It takes shared inode lock, disables page faults and iov faults around iomap DIO, retries after faulting destination pages, and returns completed read bytes.
- Fault handling is designed to avoid deadlocks on Btrfs extent locks held until read bio completion.

Alignment:
- `check_direct_IO()` requires offset and iov alignment to `fs_info->sectorsize`.

Bioset lifecycle:
- `btrfs_init_dio()` initializes `btrfs_dio_bioset`.
- `btrfs_destroy_dio()` exits the bioset.

Cross-file relationships:
- Uses delalloc reservation APIs from `delalloc-space.c`.
- Uses ordered extent lifecycle from `ordered-data.h`.
- Submits through Btrfs bio/volume mapping code.
- Relies on extent maps, COW/NOCOW checks, and transaction/block reservation helpers elsewhere in Btrfs.
