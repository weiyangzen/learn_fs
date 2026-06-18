# File Research: sources/local-fs/kdave-linux/fs/btrfs/dev-replace.c

This file implements Btrfs online device replacement: copying all existing extents from a source device to a target while duplicating new writes so the filesystem can remain mounted read-write.

High-level model:
- New writes are duplicated to source and target while replacement is active.
- Existing extents are copied using the scrub machinery.
- NOCOW hazards are avoided by marking block groups read-only/`TO_COPY` where needed, especially on zoned filesystems.
- Completion swaps source and target devices in mapping structures and device metadata.

Initialization:
- `btrfs_init_dev_replace()` reads the `BTRFS_DEV_REPLACE_KEY` item from the device tree.
- If the item is missing/corrupt, it initializes state as never started unless a dangling replace target exists.
- For active/suspended replacement, it resolves source and target devices, validates degraded/missing-device rules, and marks target as replace target/in metadata.
- Stored state includes source devid, read mode, state, timestamps, errors, cursors, and validity/writeback flags.

Target device setup:
- `btrfs_init_dev_replace_tgtdev()` opens the target path writeable, verifies zoned compatibility, rejects devices already in the filesystem, checks size, allocates a Btrfs device with special devid `BTRFS_DEV_REPLACE_DEVID`, initializes geometry/accounting, loads zone info, and links it into the device list.
- Errors close the opened block device file.

On-disk state writeback:
- `btrfs_run_dev_replace()` is called during transaction commit.
- It inserts or updates the device replace item in the device tree when `item_needs_writeback` is set.
- The function writes all mutable replace state under `dev_replace->rwsem`.

Zoned/block-group copy markers:
- `mark_block_group_to_copy()` scans source device extents from the commit root and marks corresponding block groups with `BLOCK_GROUP_FLAG_TO_COPY` on zoned filesystems.
- It waits out pending device updates by committing transactions before scanning.
- `btrfs_finish_block_group_to_copy()` clears `TO_COPY` only after the last stripe for that source device is copied.

Starting replacement:
- `btrfs_dev_replace_start()` resolves the source device, rejects active swapfile usage, commits current transaction to update device totals, creates target device, marks copy block groups, sets replace state to started, adds sysfs entry, waits ordered roots, commits the replace item, then runs scrub from offset 0 over the source device.
- After scrub, it calls `btrfs_dev_replace_finishing()`.
- Failure before scrub destroys the target replace device.

Ioctl entry:
- `btrfs_check_replace_dev_names()` validates nul-terminated source/target names.
- `btrfs_dev_replace_by_ioctl()` validates read-from-source mode, starts replacement, stores result, and maps normal/scrub-in-progress results to ioctl success.

Finishing:
- `btrfs_dev_replace_finishing()` serializes against cancel/unmount with `lock_finishing_cancel_unmount`.
- It verifies state is still started, flushes delalloc and waits ordered roots, then loops committing transactions until source device post-commit list is empty.
- It locks device list and chunk mutex to prevent super writes and new source allocations.
- On scrub success:
  - Updates target allocation state from source.
  - Rewrites mapping tree stripes from source device to target device.
  - Sets state finished, clears replacement pointers, swaps devids and UUIDs, transfers size/usage fields, updates active-device assignment, puts target on allocation list, increments rw device count, blocks bios, removes/free source, updates sysfs, scratches old superblocks, and commits superblock writeback.
- On scrub failure:
  - Sets state canceled, destroys target, unblocks bios, and returns the scrub error.

Mapping update:
- `btrfs_dev_replace_update_device_in_mapping_tree()` walks the chunk mapping rb tree under write lock and replaces stripe device pointers from source to target.
- `btrfs_set_target_alloc_state()` mirrors `CHUNK_ALLOCATED` bits from source to target extent state.

Status/progress:
- `btrfs_dev_replace_progress()` reports 0, 1000, or cursor-derived progress in thousandths.
- `btrfs_dev_replace_status()` fills ioctl status fields from in-memory state.

Cancel/suspend/resume:
- `btrfs_dev_replace_cancel()` rejects read-only mounts, handles not-started states, cancels active scrub for started state, or performs direct cleanup for suspended state.
- `btrfs_dev_replace_suspend_for_unmount()` changes started state to suspended and marks item writeback.
- `btrfs_resume_dev_replace_async()` resumes started/suspended replacements, verifies target block device exists, starts an exclusive dev-replace op, and spawns `btrfs-devrepl`.
- `btrfs_dev_replace_kthread()` resumes scrub from `committed_cursor_left`, then finishes replacement and releases exclusive op.

Ongoing/bio coordination:
- `btrfs_dev_replace_is_ongoing()` treats started and suspended states as ongoing even with missing target.
- `btrfs_rm_dev_replace_blocked()` sets filesystem replace state and waits for the percpu bio counter to drain.
- `btrfs_rm_dev_replace_unblocked()` clears the state and wakes waiters.
- `btrfs_bio_counter_sub()` subtracts bio counter and wakes waiters.
- `btrfs_bio_counter_inc_blocked()` increments unless replacement removal is blocking; if blocked, it waits and retries.

Important locking:
- `dev_replace->rwsem` protects mutable replace state.
- `lock_finishing_cancel_unmount` serializes finish, cancel, and unmount suspension.
- `device_list_mutex` and `chunk_mutex` protect device list and chunk allocation/mapping consistency during final swap.
- `mapping_tree_lock` protects chunk map updates.
