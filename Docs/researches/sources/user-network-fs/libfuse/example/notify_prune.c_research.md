# sources/user-network-fs/libfuse/example/notify_prune.c

## Purpose
`notify_prune.c` is a low-level FUSE example that exposes a single read-only file named `current_time`. The file content is a timestamp string, but the example intentionally uses very long entry and attribute timeouts plus `fi->keep_cache` to show that kernel-side dentry/inode/page-cache state can make content appear stale. A background thread calls `fuse_lowlevel_notify_prune()` for inode `FILE_INO` so the kernel prunes its cached node and sends `FORGET`; the server updates the timestamp only when lookup count falls to zero.

## Important APIs, Types, and Functions
The file uses `FUSE_USE_VERSION FUSE_MAKE_VERSION(3, 19)` and the low-level API from `fuse_lowlevel.h`. `struct fuse_lowlevel_ops tfs_oper` registers `init`, `destroy`, `lookup`, `getattr`, `readdir`, `open`, `read`, and `forget`. `struct options` is parsed with `fuse_opt_parse` for `--no-notify` and `--update-interval=%d`. `tfs_stat()` synthesizes root and file attributes. `update_fs()` fills global `file_contents` and `file_size`. `update_fs_loop()` is the notification thread and the direct integration point for `fuse_lowlevel_notify_prune()`.

## Control Flow
`main()` parses options and standard FUSE command-line flags, initializes file contents, creates and mounts a `fuse_session`, daemonizes, starts `update_fs_loop`, then runs either `fuse_session_loop` or `fuse_session_loop_mt` with a `fuse_loop_config`. Lookup of `/current_time` replies with long cache timeouts and increments `lookup_cnt`. Reads return the current global buffer through `reply_buf_limited()`. The background thread sleeps for the configured interval and, when notifications are enabled and the kernel has looked up the file, asks the kernel to prune `FILE_INO`. When the kernel later sends `forget`, `tfs_forget()` decrements `lookup_cnt` and refreshes the content at zero lookup count.

## State and Persistence
All filesystem state is process-local: `file_contents`, `file_size`, `lookup_cnt`, parsed options, and atomic `is_stop`. There is no persistent backing store. The example relies on kernel caches as observable state: entry/attr timeouts are set to `NO_TIMEOUT`, `open` sets `keep_cache`, and prune notifications force the kernel to drop awareness so a later lookup sees refreshed content. `lookup_cnt` is not protected by a mutex, so multi-threaded loops can race with the updater; this is acceptable for a small demonstration but important if reused.

## Dependencies and Integration Points
The program depends on libfuse low-level session APIs, pthreads, libc time formatting, and standard file-mode constants. It integrates with FUSE notification support through `fuse_lowlevel_notify_prune()` and tolerates `-ENOENT`, `-EBADF`, and `-ENODEV` during teardown. It also depends on FUSE sending `FORGET` requests after prune; without that behavior, `update_fs()` is not triggered by notification.

## Risks
The main correctness risk is unsynchronized access to `lookup_cnt`, `file_contents`, and `file_size` across the FUSE worker thread(s) and updater thread. The error message in `update_fs_loop()` incorrectly names `fuse_lowlevel_notify_store()` although it calls prune. `pthread_create` failure jumps to `err_out3` without unmounting first, so cleanup shape differs from the normal path. `update_interval` is not validated; zero causes a tight-ish loop with `sleep(0)`, and negative values are converted by `sleep`.

## Test Signals
Manual testing should mount with and without `--no-notify`, repeatedly `cat mnt/current_time`, and verify that the no-notify mode remains stale while notification mode changes after prune/forget cycles. Additional signals are lookup/forget balance under `-f -d`, successful unmount without aborting on expected notification errors, and behavior under both single-threaded and multi-threaded loops.
