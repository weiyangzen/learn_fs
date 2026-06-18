# sources/user-network-fs/libfuse/example/notify_inval_entry.c

## Purpose

`notify_inval_entry.c` is a low-level libfuse example for dentry invalidation. It exposes one file whose name changes to the current time and demonstrates `fuse_lowlevel_notify_inval_entry`, `fuse_lowlevel_notify_expire_entry`, and `fuse_lowlevel_notify_increment_epoch`. The source was read as a complete 427-line file.

## Important APIs, Types, and Functions

Callbacks are `tfs_init`, `tfs_lookup`, `tfs_forget`, `tfs_getattr`, and `tfs_readdir`. Other important functions are `update_fs`, `update_fs_loop`, `show_help`, and `main`. Options are `--no-notify`, `--update-interval`, `--timeout`, `--only-expire`, and `--inc-epoch`.

## Control Flow

`main` parses options, rejects mutually exclusive expire/epoch modes, initializes the file name, creates and mounts a low-level session, daemonizes, records the main thread, starts an updater thread, and runs the FUSE loop. Lookup increments `lookup_cnt`; forget decrements it. The updater saves the old name, updates to the new name, and if the kernel has a lookup, invalidates/expires/increments epoch for cached dentries.

## State and Persistence Behavior

State is volatile globals: `file_name`, `file_ino`, `lookup_cnt`, options, and `main_thread`. Kernel cache entries persist for `options.timeout` unless notifications invalidate or expire them.

## Dependencies and Integration Points

It depends on low-level libfuse, pthreads, signal handling, and time APIs. It is built as a threaded example.

## Risks and Edge Cases

`lookup_cnt` and `file_name` are shared across FUSE and updater threads without locks. The updater handles `-ENOSYS` by exiting the session and signalling the main thread, but other notification failures are asserted. There is no updater join at shutdown.

## Test Signals

Compare behavior with `--no-notify`, default invalidation, `--only-expire`, and `--inc-epoch`; test old-name stat behavior across timeout intervals, ENOSYS handling on older kernels, and lookup/forget count changes.
