# File Research: sources/local-fs/e2fsprogs/misc/fsck.h

## Purpose
Shared declarations and constants for the fsck front-end and mount-detection helper.

## Key Elements
Defines compatibility macros, default filesystem type `ext2`, array limits, fsck exit status bit constants, `struct fs_info`, `struct fsck_instance`, and flags for completed/progress-owning checks.

Declares `base_device`, `identify_fs`, and `is_mounted`.

## Dependencies
Requires standard `time.h`; used by `fsck.c` and `ismounted.c`.

## Behavior/Risks
Header centralizes hard-coded limits and status semantics. No include guard is present in this file.
