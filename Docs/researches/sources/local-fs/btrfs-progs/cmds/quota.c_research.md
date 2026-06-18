# File Research: sources/local-fs/btrfs-progs/cmds/quota.c

## Purpose

Implements the `btrfs quota` command group for enabling/disabling quota accounting, rescanning metadata, and reporting quota subsystem status.

## Commands Implemented

- `quota enable [-s|--simple] <path>`
- `quota disable <path>`
- `quota rescan [-s|-w|-W] <path>`
- `quota status [--is-enabled] <path>`

## Key Helpers

- `quota_ctl()` wraps `BTRFS_IOC_QUOTA_CTL`.
- `quota_is_enabled()` checks whether the filesystem has a qgroups sysfs directory.
- `describe_mode()` maps sysfs mode strings to user-facing descriptions.

## Important Behavior

- `quota enable --simple` uses `BTRFS_QUOTA_CTL_ENABLE_SIMPLE_QUOTA`; otherwise full qgroup accounting is enabled.
- `quota rescan -s` only reports current rescan status.
- `quota rescan -w` starts a rescan and waits for completion.
- `quota rescan -W` waits for an already-running rescan without starting one.
- `quota status --is-enabled` returns process status only and prints nothing.
- `quota status` reads sysfs files for mode, inconsistent state, quota override, drop-subtree threshold, and qgroup counts.
- For kernels without `qgroups/mode`, status assumes classic `qgroup` mode.

## External Interfaces

Uses:

- `BTRFS_IOC_QUOTA_CTL`
- `BTRFS_IOC_QUOTA_RESCAN`
- `BTRFS_IOC_QUOTA_RESCAN_STATUS`
- `BTRFS_IOC_QUOTA_RESCAN_WAIT`
- qgroup sysfs files under the filesystem fsid directory
