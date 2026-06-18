# sources/user-network-fs/libfuse/example/notify_store_retrieve.c

## Purpose
`notify_store_retrieve.c` is a low-level FUSE example for actively pushing changed file data into the kernel page cache. It exposes one read-only `current_time` file whose userspace buffer changes periodically. Unlike invalidate/prune examples, the updater calls `fuse_lowlevel_notify_store()` to store the new bytes in the kernel and then `fuse_lowlevel_notify_retrieve()` to ask the kernel to send the stored bytes back for verification.

## Important APIs, Types, and Functions
The file uses `FUSE_USE_VERSION FUSE_MAKE_VERSION(3, 12)`, `struct fuse_lowlevel_ops`, and `struct fuse_bufvec`. `tfs_lookup()`, `tfs_forget()`, `tfs_getattr()`, `tfs_readdir()`, `tfs_open()`, and `tfs_read()` implement the single-file filesystem. `tfs_retrieve_reply()` is registered as `.retrieve_reply` and validates retrieved data with `fuse_buf_copy()`. `update_fs_loop()` performs `fuse_lowlevel_notify_store()` and `fuse_lowlevel_notify_retrieve()` while holding a mutex over lookup/open counters and the buffer setup.

## Control Flow
`main()` parses options, prepares the first timestamp, creates/mounts a low-level session, starts the updater thread, and enters the selected FUSE loop. Lookups reply with very long entry and attr timeouts; only after a successful reply does the code increment `lookup_cnt`. Opens set `keep_cache` and increment `open_cnt`. The updater refreshes `file_contents`, and if notifications are enabled and both `open_cnt` and `lookup_cnt` are positive, it stores the buffer in the kernel page cache and schedules a retrieve request using a duplicated expected string as cookie. On destroy, `is_umount` is set and the updater is joined.

## State and Persistence
State is in global process memory: current string, file size, lookup/open counts, mutex, `retrieve_status`, unmount flag, and updater TID. There is no disk persistence. The important external state is the kernel page cache, which receives stored bytes and later returns them through `retrieve_reply`. `retrieve_status` encodes whether data was stored but not yet validated (`1`) or validated (`2`); `main()` asserts that shutdown does not leave it stuck at `1`.

## Dependencies and Integration Points
This example integrates with FUSE notification APIs that require the kernel to know the node and usually require an open cached file to demonstrate effects. It uses pthreads for the producer thread and `fuse_bufvec` for zero-copy-ish buffer plumbing. It tolerates expected notification failures during unmount (`ENOENT`, `EBADF`, `ENODEV`) but otherwise aborts.

## Risks
`open_cnt` increments on open but is never decremented on release because no release handler exists; for a demo this keeps notification active, but a real server would leak open state. The assertion after `fuse_lowlevel_notify_retrieve()` contains `ret != -ENODEV`, likely intended to be `ret == -ENODEV`, so it does not symmetrically accept that teardown error. `retrieve_status` is written outside the mutex in `tfs_retrieve_reply()`, so it can race with shutdown assertions. `file_contents` is updated before taking `lock`, while reads access it without locking.

## Test Signals
Run with `--no-notify` and confirm repeated reads stay at the initially cached timestamp. Run without it and confirm reads advance once per update interval. Debug logs or breakpoints should show `retrieve_reply` setting `retrieve_status` to `2`. Teardown tests should unmount during active notification and confirm only expected kernel-side errors are accepted.
