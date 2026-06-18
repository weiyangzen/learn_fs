# sources/user-network-fs/libfuse/lib/mount_util.h

## Purpose
Header for shared mount utility functionality and the canonical mount option metadata table.

## Important APIs, Types, And Functions
- `struct mount_flags` records option name, bit flag, enabled/disabled sense, non-root safety, fsconfig applicability, and mount-attribute mapping.
- Declares mtab/umount helpers, path resolver, fuseblk support probe, `/dev/fd` parser, device selector, mtab helper, and source/type builders.

## Control Flow
No executable flow. The struct fields drive option-processing loops in `mount.c`, `mount_fsmount.c`, `fusermount.c`, and `mount_service.c`.

## State And Persistence
No state. Declared functions may update mount tables and allocate returned strings; callers own strings from builder/resolver functions.

## Dependencies And Integration Points
Includes `mount_common_i.h` so users can see internal mount option APIs. It is part of both library and utility builds, including setuid helpers.

## Risks
Changing `mount_flags` semantics affects security filtering in helpers and option translation in the new mount API. Adding flags without classifying `safe`, `is_fsconfig`, and `mount_attr` can silently widen non-root behavior or break fsconfig.

## Test Signals
Static compile users after adding flags, and run option matrix tests across direct mount, fusermount, and service mount paths.
