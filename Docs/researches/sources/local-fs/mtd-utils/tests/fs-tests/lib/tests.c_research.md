# File Research: sources/local-fs/mtd-utils/tests/fs-tests/lib/tests.c

## Purpose
Shared runtime library for the mtd-utils filesystem test programs.

## Key Elements
Provides common argument parsing (`-z/-n/-p/-s/-u/-o/-c/-e`), mount-directory/type setup from environment, assertion reporting, free/total space queries, deterministic filled-file and fragment-file writers/checkers, orphan creation, directory cleanup, random entry create/remove helpers, remount/unmount/mount helpers, root/current-FS checks, and PID-safe name building.

## Dependencies
Uses POSIX file APIs, `statvfs/statfs`, mount table parsing, Linux mount flags, `linux/fs.h`, `linux/jffs2.h`, and `tests.h`.

## Behavior/Risks
Designed for destructive tests under `TEST_FILE_SYSTEM_MOUNT_DIR` defaulting to `/mnt/test_file_system`. It allows root filesystem tests by default because `tests_get_args()` sets `rootok = 1`, and many cleanup routines depend on `dirent.d_type`.
