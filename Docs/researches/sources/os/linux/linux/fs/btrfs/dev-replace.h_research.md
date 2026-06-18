# File Research: sources/os/linux/linux/fs/btrfs/dev-replace.h

This header declares the public device replacement API.

Exported operations:
- Initialization and transaction writeback: `btrfs_init_dev_replace()` and `btrfs_run_dev_replace()`.
- Ioctl entry points: `btrfs_dev_replace_by_ioctl()`, `btrfs_dev_replace_status()`, and `btrfs_dev_replace_cancel()`.
- Mount/unmount lifecycle: `btrfs_dev_replace_suspend_for_unmount()` and `btrfs_resume_dev_replace_async()`.
- State query: `btrfs_dev_replace_is_ongoing()`.
- Zoned/block-group support: `btrfs_finish_block_group_to_copy()`.
- Bio quiescing helpers: `btrfs_bio_counter_inc_blocked()`, `btrfs_bio_counter_sub()`, and inline `btrfs_bio_counter_dec()`.

Design notes:
- The header forward declares ioctl, filesystem, transaction, replace, block group, and device structures to keep dependencies narrow.
- The `__pure` attribute on `btrfs_dev_replace_is_ongoing()` indicates the query depends only on the passed replace structure state.
