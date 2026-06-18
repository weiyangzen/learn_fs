# sources/test-tools/fio/engines/nfs.c

## Purpose
Implements an asynchronous NFS engine using libnfs. It mounts an NFS URL, opens fio file paths on that mount, queues asynchronous pread/pwrite operations, and buffers completions for fio's event loop.

## Important APIs, Types, And Functions
`struct fio_libnfs_options` stores the shared libnfs context, URL, queue depth, outstanding/buffered completion counters, circular event-buffer indexes, and event array. `struct nfs_data` stores an opened NFS file handle and pointer back to options. Key functions are `do_mount()`, `fio_libnfs_setup()`, `fio_libnfs_open()`, `fio_libnfs_queue()`, `nfs_callback()`, `nfs_event_loop()`, `fio_libnfs_getevents()`, `fio_libnfs_event()`, `fio_libnfs_close()`, and `fio_libnfs_cleanup()`.

## Control Flow
`setup` disables fio thread mode because libnfs can hang on threaded exit. `open` requires `nfs_url`, mounts once per job through `do_mount()`, allocates per-file state, and opens the NFS file. Queue attaches the per-file state to `io_u`, calls libnfs async read or write with API-version-dependent argument order, and increments `outstanding_events`. The libnfs callback copies read data into the fio buffer, sets error/residual fields, and appends the `io_u` to a circular completion buffer. `getevents` services the libnfs fd via `poll()` and `nfs_service()` until completions are buffered or queue pressure is relieved. `event` returns completions in buffered order and validates sequential fio event requests with asserts.

## State And Persistence
The NFS context and completion buffer are stored in option state. Per-file engine data owns each `nfsfh`. Persistent effects are remote NFS writes. The engine does not support trim.

## Dependencies And Integration Points
Depends on libnfs headers, fio event callbacks, fio option state, and POSIX `poll()`. It marks itself diskless/noextend/no diskutil.

## Risks
`do_mount()` assumes `nfs_parse_url_full()` succeeds and builds mount path by concatenating URL path and file. Completion buffers are assert-heavy rather than gracefully bounded. `fio_libnfs_getevents()` ignores `min`, `max`, and timeout arguments and returns whatever the event loop has buffered. Cleanup assumes context was mounted. EOF on read is logged as likely unexpected.

## Test Signals
Test missing and malformed `nfs_url`, mount/open failure, LIBNFS API v1/v2 builds, read/write completions, EOF reads, event ordering assertions, queue-depth saturation, trim rejection, cleanup after partial open, and non-threaded multi-job behavior.
