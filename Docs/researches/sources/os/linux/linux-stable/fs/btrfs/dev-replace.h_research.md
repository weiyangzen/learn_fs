# File Research: sources/os/linux/linux-stable/fs/btrfs/dev-replace.h

This header declares the Btrfs device replacement interface.

Public API:
- Lifecycle and persistence:
  - `btrfs_init_dev_replace()`
  - `btrfs_run_dev_replace()`
  - `btrfs_resume_dev_replace_async()`
  - `btrfs_dev_replace_suspend_for_unmount()`
- Ioctl-facing operations:
  - `btrfs_dev_replace_by_ioctl()`
  - `btrfs_dev_replace_status()`
  - `btrfs_dev_replace_cancel()`
- State helpers:
  - `btrfs_dev_replace_is_ongoing()`
  - `btrfs_finish_block_group_to_copy()`
- Bio synchronization:
  - `btrfs_bio_counter_inc_blocked()`
  - `btrfs_bio_counter_sub()`
  - `btrfs_bio_counter_dec()`

Forward declarations keep this interface independent of full structure definitions:
- `btrfs_ioctl_dev_replace_args`
- `btrfs_fs_info`
- `btrfs_trans_handle`
- `btrfs_dev_replace`
- `btrfs_block_group`
- `btrfs_device`

Role in Btrfs:
The header exposes replace control, status, resume, block-group progress, and bio-counter primitives to transaction, ioctl, scrub, mapping, and unmount paths.
