# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_volume.c

HAMMER1 volume management implementation for adding, deleting, listing, formatting, freeing, and accounting non-root filesystem volumes.

Key responsibilities:
- Implements `hammer_ioc_volume_add()` for adding a new block device as a HAMMER volume.
- Implements `hammer_ioc_volume_del()` for removing a non-root volume, optionally reblocking live data off the volume first.
- Implements `hammer_ioc_volume_list()` for returning mounted volume numbers and device names to userspace.
- Formats new volume headers by copying filesystem identity, version, label, signature, root volume number, and layout parameters from the root volume.
- Initializes freemap layer1/layer2 entries for newly added volumes and frees freemap metadata for removed volumes.
- Counts total and empty big-blocks in a volume and updates root-volume filesystem statistics after volume add/remove.
- Drives full-filesystem reblock work when deleting a non-empty volume with `HAMMER_IOC_VOLUME_REBLOCK`.

Important implementation details:
- Volume add/delete operations are serialized by `hmp->volume_lock`.
- Structural freemap mutations run under `hammer_sync_lock_sh(trans)` and `hmp->blkmap_lock`.
- Added volumes are assigned the first unused volume number below `HAMMER_MAX_VOLUMES`.
- Root volume removal is forbidden, and deletion is refused if the target volume is non-empty unless reblock is requested.
- `hammer_format_freemap()` allocates layer1 blocks for the new volume, marks freemap-reserved big-blocks, marks usable big-blocks free, and marks tail-aligned space unavailable.
- `hammer_free_freemap()` first verifies that all non-freemap/non-unavailable big-blocks are empty, then clears layer2 entries and marks layer1 unavailable.
- Volume removal unloads cached buffers associated with the volume, unloads the volume, decrements volume count, and adjusts root statistics.

Dependencies:
- Uses HAMMER1 transaction, blockmap, volume, buffer, CRC, flusher, reblock, sync, and mount-stat APIs through `hammer.h`.
- Interacts with userspace ioctl payloads `hammer_ioc_volume` and `hammer_ioc_volume_list`.
- Depends on HAMMER freemap geometry macros such as `HAMMER_BLOCKMAP_LAYER1_OFFSET`, `HAMMER_BLOCKMAP_LAYER2_OFFSET`, `HAMMER_BIGBLOCK_SIZE`, and encoded raw volume offsets.

Notable risks:
- Comments note that freemap formatting/freeing uses `hammer_modify_buffer()` and can theoretically pressure or overwrite the UNDO FIFO for large devices.
- Deletion contains an explicit three-pass `hammer_flusher_sync()` workaround before unloading buffers, indicating historically fragile synchronization.
- Freemap accounting assumes non-root volumes and asserts heavily on layer state; corrupted freemap state may panic rather than degrade gracefully.
- User-visible deletion depends on exact volume device-name matching.
- Volume statistics and mount stat block counts must remain synchronized with root-volume on-disk header updates.
