# File Research: sources/os/linux/linux-stable/fs/btrfs/dev-replace.c

This file implements Btrfs device replacement. It copies existing extents from a source device to a target device while the filesystem remains writable, duplicates new writes during the replacement window, persists replace state, and swaps the target into the filesystem at completion.

Design:
- Existing committed extents are copied by scrub.
- New writes are duplicated to both source and target via mapping logic outside this file.
- NOCOW hazards are handled by marking block groups read-only/to-copy where needed.
- Completion swaps source and target device identities and mapping-tree references.
- Cancel, suspend, and resume paths preserve or clean persistent replace state.

Initialization:
- `btrfs_init_dev_replace()` reads the `BTRFS_DEV_REPLACE_KEY` item from the device root.
- Missing or corrupt replace items initialize the state to `NEVER_STARTED`, unless a replace target device is found, which is treated as filesystem inconsistency.
- Active `STARTED` or `SUSPENDED` states resolve source and target devices and set target geometry/state.

Target setup:
- `btrfs_init_dev_replace_tgtdev()` opens the target block device writable, checks zoned compatibility, rejects devices already in the filesystem, checks size, allocates a `btrfs_device`, initializes geometry/accounting, gets zone info, and links it into `fs_devices`.

Persistent state:
- `btrfs_run_dev_replace()` writes in-memory replace state back to the device tree during transaction commit.
- It creates or rewrites the dev-replace item, stores source devid, state, read mode, timestamps, error counters, and cursors.

Zoned block-group handling:
- `mark_block_group_to_copy()` marks block groups that have source-device extents with `BLOCK_GROUP_FLAG_TO_COPY` on zoned filesystems.
- `btrfs_finish_block_group_to_copy()` clears the flag once the last relevant stripe on the source device is copied.

Start path:
- `btrfs_dev_replace_start()` resolves the source device, rejects active swapfile usage, commits pending transactions for stable device byte counters, initializes the target, marks block groups to copy, sets replace state to `STARTED`, adds sysfs device state, waits ordered roots, commits the replace item, runs scrub over the source device, then calls finishing.
- `btrfs_dev_replace_by_ioctl()` validates ioctl arguments and source/target names before calling start.

Finishing path:
- `btrfs_dev_replace_finishing()` serializes against cancel/unmount, verifies `STARTED`, flushes delalloc and ordered roots, repeatedly commits until source post-commit work is clear, locks device list and chunk mutex, sets final state, and either cleans up on scrub failure or performs the swap.
- On success it:
  - Copies allocation state from source to target.
  - Updates all chunk maps to point source stripes at target.
  - Swaps devids and UUIDs.
  - Copies byte accounting.
  - Assigns active device replacement.
  - Adds target to alloc list and rw device count.
  - Blocks new bios during source removal.
  - Removes source from filesystem metadata.
  - Updates sysfs entries.
  - Scratches source superblocks if writable.
  - Commits superblocks and frees source device.

Mapping tree update:
- `btrfs_dev_replace_update_device_in_mapping_tree()` walks the chunk mapping rbtree under `chunk_mutex` and `mapping_tree_lock`, replacing source device pointers with target device pointers.

Status:
- `btrfs_dev_replace_progress()` returns progress in per-mille.
- `btrfs_dev_replace_status()` fills ioctl status fields with state, timestamps, errors, and progress.

Cancel/suspend/resume:
- `btrfs_dev_replace_cancel()` cancels active scrub or cleans up suspended replace state and commits cancellation.
- `btrfs_dev_replace_suspend_for_unmount()` changes `STARTED` to `SUSPENDED` and marks state for writeback.
- `btrfs_resume_dev_replace_async()` resumes started/suspended replace in a kernel thread if the target is present and no conflicting exclusive operation is running.
- `btrfs_dev_replace_kthread()` resumes scrub from `committed_cursor_left`, finishes replacement, and releases exclusive operation state.
- `btrfs_dev_replace_is_ongoing()` reports active/suspended replace as ongoing even if target is missing.

Bio synchronization:
- `btrfs_rm_dev_replace_blocked()` sets filesystem replacing state and waits for in-flight replace-protected bios to drain.
- `btrfs_rm_dev_replace_unblocked()` clears the blocked state and wakes waiters.
- `btrfs_bio_counter_inc_blocked()`, `btrfs_bio_counter_sub()`, and `btrfs_bio_counter_dec()` protect bio submission during replace device removal/swap.

Concurrency:
- `dev_replace->rwsem` protects replace state fields.
- `dev_replace->lock_finishing_cancel_unmount` serializes finish, cancel, and unmount suspension.
- `fs_devices->device_list_mutex`, `fs_info->chunk_mutex`, and `mapping_tree_lock` protect device and chunk mapping changes.
- A percpu bio counter gates device removal against in-flight I/O.

Role in Btrfs:
This file implements online device migration/replacement with persistent crash-resumable state, scrub-based copying, write duplication, and careful final device identity swap.
