# sources/user-network-fs/libfuse/example/notify_inval_inode.c

## Purpose

`notify_inval_inode.c` is a low-level libfuse example for inode data/attribute cache invalidation. It exposes `current_time`, keeps file data cached, updates the backing content in a background thread, and calls `fuse_lowlevel_notify_inval_inode` so later reads fetch updated contents. The source was read as a complete 402-line file.

## Important APIs, Types, and Functions

Callbacks are `tfs_init`, `tfs_destroy`, `tfs_lookup`, `tfs_forget`, `tfs_getattr`, `tfs_readdir`, `tfs_open`, and `tfs_read`. Other key functions are `update_fs`, `update_fs_loop`, `show_help`, and `main`. Globals include `file_contents`, `lookup_cnt`, `file_size`, and atomic `is_stop`.

## Control Flow

`main` parses options, initializes contents, creates/mounts a low-level session, daemonizes, starts the updater thread, and enters the FUSE loop. Lookup increments lookup count and gives very long attr/entry timeouts. Open sets `keep_cache`. The updater refreshes the time string and, if notification is enabled and the kernel knows the inode, invalidates the inode's whole cached range.

## State and Persistence Behavior

All file data is volatile globals. Kernel cache persistence is intentionally long (`NO_TIMEOUT`) unless invalidated. `tfs_destroy` flips `is_stop` so the updater can exit after session teardown.

## Dependencies and Integration Points

It depends on low-level libfuse, pthreads, C11 atomics, and time APIs. It is built as a threaded example.

## Risks and Edge Cases

`lookup_cnt`, `file_contents`, and `file_size` are not protected by locks. The updater accepts ENOENT/EBADF/ENODEV during unmount but aborts on other notification errors. The error message mentions `notify_store` despite calling `notify_inval_inode`, a minor diagnostic mismatch.

## Test Signals

Run with and without `--no-notify`, repeatedly read cached contents, vary update interval, unmount during updates, check acceptable notification errors, and run under thread sanitizer to observe demonstration-level data races.
