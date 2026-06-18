# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_blockmap.c

This file implements HAMMER’s blockmap allocation, reservation, free, dedup accounting, lookup verification, and space-checking logic. The blockmap maps logical HAMMER zone offsets through layered free-space metadata to physical zone-2 storage and coordinates crash-safe reuse of big-blocks.

Core structures used:
- Per-mount blockmaps from `hmp->blockmap[]`.
- Freemap layer1 entries, which point to layer2 blocks and track free big-block counts.
- Freemap layer2 entries, one per big-block, tracking owning zone, append offset, free bytes, and CRC.
- `hammer_reserve` RB tree keyed by zone-2 big-block base offset.
- Delay list reservations used to prevent unsafe reuse before flusher cycles complete.

Main functions:
- `hammer_blockmap_alloc()`: backend allocation from a zone.
- `hammer_blockmap_reserve()`: frontend reservation without committing metadata, mainly for direct-write paths.
- `hammer_blockmap_reserve_complete()`: reference release and possible buffer invalidation for reserved big-blocks.
- `hammer_reserve_clrdelay()`: removes delayed reservations when their flush point is reached.
- `hammer_blockmap_free()`: frees allocated space and may reset entirely-free big-blocks.
- `hammer_blockmap_dedup()`: adjusts accounting for deduplicated references, allowing `bytes_free` to become negative.
- `hammer_blockmap_finalize()`: commits a previously reserved range into the blockmap.
- `hammer_blockmap_getfree()`: reports approximate free bytes in a big-block for reblocker use.
- `hammer_blockmap_lookup_verify()`: validates layer1/layer2 metadata and returns translated zone-2 offset.
- `_hammer_checkspace()`: computes reserved/dirty/slop pressure against copied free-big-block statistics.
- `hammer_check_volume()` and `hammer_skip_volume()`: handle unavailable volume ranges and volume wrapping.

Allocation behavior:
- Request sizes are aligned with `HAMMER_DATA_DOALIGN`.
- Allocations are constrained not to cross buffer boundaries, and large allocations must not cross big-block boundaries.
- Optional hints are honored only while they stay in the hinted big-block and requested zone.
- The allocator skips full layer1 ranges, unavailable volume ranges, layer2 entries owned by another zone, entries whose append offset is past the candidate offset, and big-blocks reserved by other zones.
- Metadata updates are protected by `hmp->blkmap_lock`, but layer reads and CRC checks occur before lock acquisition and are revalidated around races.
- When a layer2 big-block is first claimed, layer1 free count and root-volume free-big-block statistics are decremented.
- `blockmap->next_offset` is advanced when no usable external hint was supplied.

Reservation behavior:
- `hammer_blockmap_reserve()` reserves address space and advances the zone’s `next_offset` without updating layer1/layer2 ownership/free-byte metadata.
- Reservations prevent other zones or allocation paths from using the same big-block range before finalization.
- If a reserved big-block is entirely free at layer2, the reservation records `HAMMER_RESF_LAYER2FREE`, enabling later invalidation/deletion of stale buffers.
- `hammer_blockmap_finalize()` assigns layer2 ownership if needed, decrements free bytes, clears layer2-free reservation state, and raises `append_off` to cover the finalized range.

Free/reuse safety:
- `hammer_blockmap_free()` increments layer2 free bytes. When the entire big-block becomes free, it installs a delayed reservation before resetting layer2 zone and append state.
- Delayed reservations avoid crash-recovery hazards where an old UNDO/REDO state could resurrect a block already reused and overwritten.
- `hammer_blockmap_reserve_complete()` can delete related HAMMER buffers for a fully-free reserved big-block, but if buffer deletion conflicts it requeues the reservation on the delay list.

CRC and corruption handling:
- Layer1 and layer2 CRCs are tested on read. If an initial test fails, the blockmap lock is acquired and the test is retried before panic.
- Layer1/layer2 CRCs are regenerated after metadata modifications.
- Lookup verification asserts zone consistency and handles the special case where layer2 is unassigned but a matching reservation exists.

Space accounting:
- `_hammer_checkspace()` estimates pressure from reserved inodes, reserved records, reserved data bytes, delayed reservations, dirty buffer limits, and caller-provided slop.
- Free space is checked against `hmp->copy_stat_freebigblocks`, a mount-level copy of root-volume free-big-block state.
