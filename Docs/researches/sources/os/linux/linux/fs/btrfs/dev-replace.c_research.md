# File Research: sources/os/linux/linux/fs/btrfs/dev-replace.c

This file implements Btrfs online device replacement. Replacement keeps the filesystem writable by duplicating new writes to both source and target while scrub copies already-existing extents from the source to the target, then the finishing path swaps device identities and mapping references.

On-disk state and mount initialization:
- `btrfs_init_dev_replace()` reads the `BTRFS_DEV_REPLACE_KEY` item from the device tree.
- Missing or malformed replace state is tolerated only when no replace target device is present.
- Active `STARTED` or `SUSPENDED` state reconnects source and target devices by devid, sets replace target flags, and initializes target geometry from the source when possible.
- Missing source or target devices cause mount failure unless the filesystem is mounted degraded.

Starting replacement:
- `btrfs_dev_replace_by_ioctl()` validates ioctl options and device-name termination before calling `btrfs_dev_replace_start()`.
- `btrfs_dev_replace_start()` locates the source device, rejects active swapfile use, commits any current transaction so device size accounting is current, initializes the target device, and marks zoned block groups for copying when needed.
- `btrfs_init_dev_replace_tgtdev()` opens the target block device writable, validates zoned compatibility, rejects a target already in the filesystem, checks it is not smaller than the source, allocates a Btrfs device object, initializes device fields, attaches zone info, and links it into the fs devices list.
- Once state is switched to `STARTED`, new writes are duplicated by the volume mapping layer.
- The code waits for ordered roots, commits the replace item to disk, then starts `btrfs_scrub_dev()` over the source device with the replace flag set.

Zoned handling:
- `mark_block_group_to_copy()` scans committed device extents for the source device and marks corresponding block groups with `BLOCK_GROUP_FLAG_TO_COPY`.
- `btrfs_finish_block_group_to_copy()` clears that flag only after the last stripe on the source device for a block group has been copied.
- This protects against unsafe NOCOW writes while replace is copying committed extents on zoned filesystems.

Persisting replace state:
- `btrfs_run_dev_replace()` is called from transaction commit when `item_needs_writeback` is set.
- It creates or updates the device replace item with source devid, read mode, state, timestamps, error counters, and copy cursors.
- It handles too-small legacy/corrupt items by deleting and reinserting a correctly sized item.

Finishing:
- `btrfs_dev_replace_finishing()` serializes against cancel/unmount, flushes delalloc and ordered roots, commits until source-device post-commit work is drained, then blocks new bios while the source and target are swapped.
- On success it copies allocation state to the target, updates the mapping tree to replace source device pointers with target device pointers, swaps devids and UUIDs, moves allocation-list membership, updates active device selection, removes the old source device, updates sysfs, scratches old superblocks, commits final superblock state, and frees the old source device.
- On scrub failure or cancellation it marks the replace canceled and destroys the target device.

Status, cancel, suspend, and resume:
- `btrfs_dev_replace_progress()` reports progress in thousandths from the copy cursor and source size.
- `btrfs_dev_replace_status()` fills ioctl status fields under the replace rwsem.
- `btrfs_dev_replace_cancel()` handles active and suspended cancellation. Active cancellation asks scrub to cancel and lets finishing cleanup run; suspended cancellation performs cleanup directly.
- `btrfs_dev_replace_suspend_for_unmount()` changes `STARTED` to `SUSPENDED` and marks the replace item dirty.
- `btrfs_resume_dev_replace_async()` resumes `STARTED` or `SUSPENDED` replacement, validates the target, starts the exclusive device replace operation, and launches `btrfs_dev_replace_kthread()`.
- The kthread restarts scrub from `committed_cursor_left`, runs finishing, and ends the exclusive operation.

Bio quiescing:
- `btrfs_bio_counter_inc_blocked()` increments the replace bio counter but waits if `BTRFS_FS_STATE_DEV_REPLACING` is set.
- `btrfs_bio_counter_sub()` decrements and wakes waiters.
- Finishing uses these counters to wait for in-flight bios before removing/swapping devices.
