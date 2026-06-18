# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_message.h

## Purpose
Declares and wraps XFS logging helpers used throughout the filesystem.

## Main Contents
Defines level-specific macros `xfs_emerg`, `xfs_alert`, `xfs_crit`, `xfs_err`, `xfs_warn`, `xfs_notice`, `xfs_info`, and debug-only `xfs_debug`. It also defines rate-limited and once-only wrappers, alert-tag logging, assertion function declarations, hex dump support, buffer alert rate limiting, and the experimental feature enum.

## Integration
The macros emit printk index metadata and dispatch to `xfs_printk_level`, preserving subsystem-indexed format strings while keeping mount-aware formatting in the implementation.
