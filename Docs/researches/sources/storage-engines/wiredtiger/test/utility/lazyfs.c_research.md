# sources/storage-engines/wiredtiger/test/utility/lazyfs.c

## Purpose

`lazyfs.c` integrates tests with LazyFS, a Linux FUSE filesystem used to inject/cache filesystem behavior. It can locate LazyFS, create its config, mount/unmount it, send control commands, and set up/clean up a LazyFS-backed WiredTiger home.

## Important APIs, Types, and Functions

Functions include `lazyfs_is_implicitly_enabled`, `lazyfs_init`, `lazyfs_create_config`, `lazyfs_mount`, `lazyfs_unmount`, `lazyfs_command`, `lazyfs_clear_cache`, `lazyfs_display_cache_usage`, `testutil_lazyfs_setup`, `testutil_lazyfs_clear_cache`, and `testutil_lazyfs_cleanup`.

## Control Flow

Setup initializes LazyFS path relative to the current executable, canonicalizes the test home, creates a base directory, creates a temporary control FIFO path under `/tmp`, writes LazyFS config, and forks/execls LazyFS with a subdir module. The parent waits until the mount point is mounted. Cleanup unmounts through LazyFS scripts, waits for the child, and removes control/mount paths.

## State and Persistence Behavior

State lives in `WT_LAZY_FS` path fields, the LazyFS config/log/control files, the base backing directory, the mount point, and child process PID. Control commands write `lazyfs::<command>` lines to the control file.

## Dependencies and Integration Points

Linux-only paths depend on `/proc/self/exe`, `prctl(PR_SET_PDEATHSIG)`, fork/exec/wait, `is_mounted`, `testutil_system`, LazyFS build layout, and constants from `test_util.h`.

## Risks and Edge Cases

Non-Linux functions fail with ENOENT. Mounting requires LazyFS to be built at the expected relative path and may need FUSE permissions such as `allow_other`. The child kills the parent on setup errors to avoid orphaned mounts.

## Test Signals

Signals are successful mount detection, working cache control commands, LazyFS log/config creation, and clean unmount/removal during cleanup.
