# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass2.c

This file implements phase 2: pathname and directory structure validation.

Key behavior:
- Ensures the root inode exists and is a directory, reallocating or fixing mode when approved.
- Marks root as `DFOUND` and whiteout inode `UFS_WINO` as a whiteout file state.
- Sorts directory cache entries by first disk block to improve scanning locality.
- Validates every cached directory with `pass2check()`.
- Repairs directory length too short or not a multiple of `DIRBLKSIZ`.
- Builds temporary directory dinodes from cached block lists to scan directory data.
- After scanning entries, verifies and repairs each directory’s `..` against discovered parent.
- Propagates root reachability through the directory tree.

`pass2check()`:
- Checks and repairs `.` entry inode/type.
- Checks, adds, replaces, or defers `..`.
- Removes extra `.` or `..` entries.
- Removes out-of-range or unallocated directory entries.
- Repairs whiteout entries and bad type values.
- Handles entries pointing to `DCLEAR`/`FCLEAR` objects.
- Tracks parent relationships and decrements link counts for observed references.
- Detects and fixes extraneous hard links to directories.

`fix_extraneous()`:
- Determines whether a duplicate directory name or old parent name should be removed based on `..`.
- In snapshot/background paths, uses sysctls plus `unlink`.
- In foreground paths, edits directory entries directly.

Important interactions:
- Consumes directory cache from pass 1 and produces parent/dotdot/depth state for pass 3.
- Updates link-count residuals used by pass 4.
- Uses live sysctl operations when checking snapshots/background filesystems.
