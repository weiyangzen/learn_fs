# File Research: sources/local-fs/btrfs-progs/check/qgroup-verify.h

## Purpose
Declares the qgroup verification API used by the btrfs check code.

## API
- `qgroup_verify_all(struct btrfs_fs_info *info)` verifies all quota-group accounting for a filesystem.
- `report_qgroups(int all)` prints qgroup accounting differences after verification.
- `repair_qgroups(struct btrfs_fs_info *info, int *repaired, bool silent)` writes repaired qgroup info/status items.
- `print_extent_state(struct btrfs_fs_info *info, u64 subvol)` prints extent ownership state for one subvolume.
- `free_qgroup_counts()` frees retained qgroup count records.
- `qgroup_set_item_count_ptr(u64 *item_count_ptr)` installs an optional progress/item counter.

## Dependencies
Includes `kerncompat.h`, `stdbool.h`, and forward-declares `struct btrfs_fs_info`.
