# File Research: sources/virtualization/libguestfs/daemon/xfs.c

## Role
Implements XFS-specific daemon helpers for growfs, admin metadata changes, UUID/label setters, and minimum-size reporting.

## Main Operations
- `optgroup_xfs_available()` checks for `mkfs.xfs`.
- `do_xfs_growfs()` maps a mount path through `sysroot_path()` and builds an `xfs_growfs` command with optional data/log/realtime sizing controls.
- `do_xfs_admin()` wraps `xfs_admin` for feature flags, lazycounter, label, and UUID options.
- `xfs_set_uuid()`, `xfs_set_uuid_random()`, and `xfs_set_label()` configure `optargs_bitmask` and delegate to `do_xfs_admin()`.
- `xfs_minimum_size()` returns the current XFS data section size because XFS does not support shrinking.

## Validation
Numeric size and percentage arguments must be nonnegative. XFS labels are limited by `XFS_LABEL_MAX`. Minimum-size computation checks for integer overflow.

## Filesystem/Storage Relevance
This file handles XFS grow and metadata operations used during guest filesystem resize, relabeling, and UUID management workflows.
