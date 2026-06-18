# File Research: sources/local-fs/kdave-linux/fs/btrfs/dev-replace.h

This header exports the Btrfs device replacement API.

Declared operations:
- Lifecycle/state:
  - `btrfs_init_dev_replace()`
  - `btrfs_run_dev_replace()`
  - `btrfs_dev_replace_is_ongoing()`
- User operations:
  - `btrfs_dev_replace_by_ioctl()`
  - `btrfs_dev_replace_status()`
  - `btrfs_dev_replace_cancel()`
- Mount/unmount/resume:
  - `btrfs_dev_replace_suspend_for_unmount()`
  - `btrfs_resume_dev_replace_async()`
- Zoned/block-group completion:
  - `btrfs_finish_block_group_to_copy()`
- Bio drain coordination:
  - `btrfs_bio_counter_inc_blocked()`
  - `btrfs_bio_counter_sub()`
  - Inline `btrfs_bio_counter_dec()` wrapper.

Design notes:
- Uses forward declarations for ioctl args, fs info, transaction handle, device replace state, block group, and device.
- Marks `btrfs_dev_replace_is_ongoing()` as `__pure`.
