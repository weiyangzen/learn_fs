# sources/user-network-fs/libfuse/example/invalidate_path.c

## Purpose

`invalidate_path.c` is a high-level libfuse example for path-based cache invalidation. It exposes dynamic files `current_time` and `growing`, gives the kernel very long entry/attr timeouts, then uses `fuse_invalidate_path` from a background thread so changes become visible. The source was read as a complete 292-line file.

## Important APIs, Types, and Functions

Callbacks in `xmp_oper` are `xmp_init`, `xmp_getattr`, `xmp_readdir`, `xmp_open`, and `xmp_read`. Other key functions are `update_fs`, `invalidate`, `update_fs_loop`, `show_help`, and `main`. Options are `--no-notify` and `--update-interval`.

## Control Flow

`main` initializes contents, parses options/cmdline, mounts, daemonizes, starts an updater thread, installs signal handlers, and enters a FUSE loop. The updater refreshes the time string and growing size, then invalidates both paths unless notifications are disabled. Reads serve the current memory state.

## State and Persistence Behavior

State is volatile globals: `time_file_contents`, `grow_file_size`, and options. Kernel cache persistence is intentionally long (`NO_TIMEOUT`) so invalidation behavior is observable.

## Dependencies and Integration Points

It depends on high-level libfuse, low-level cmdline helpers, pthreads, and time APIs.

## Risks and Edge Cases

The updater thread is not joined or explicitly stopped. Dynamic globals are read by callbacks and written by the updater without locking, making races possible. Read calculations can underflow when offsets exceed dynamic file sizes.

## Test Signals

Mount with and without `--no-notify`, repeatedly read/stat both files, vary update interval, exercise single-thread/multi-thread loops, and verify invalidation treats `-ENOENT` as benign.
