# sources/user-network-fs/libfuse/example/poll.c

## Purpose
`poll.c` demonstrates high-level FUSE poll/select support for readiness changes generated outside kernel file writes. It exposes sixteen read-only files named `0` through `F`; a producer thread periodically adds bytes to their counters and notifies poll waiters.

## Important APIs, Types, and Functions
`fsel_oper` registers `destroy`, `getattr`, `readdir`, `open`, `release`, `read`, and `poll`. Global arrays track per-file counts and `struct fuse_pollhandle *` values. `fsel_poll()` records poll handles and sets readiness bits. `fsel_producer()` mutates counters and calls `fuse_notify_poll()` followed by `fuse_pollhandle_destroy()`.

## Control Flow
`main()` initializes the mutex and starts the producer thread before entering `fuse_main`. `open` maps paths `/0` to `/F` to a numeric file handle and allows only one open per file by `fsel_open_mask`; files are direct I/O and nonseekable. `read` consumes up to the requested size from the per-file count and fills the buffer with the file's hex character. `poll` records a handle when provided and immediately reports `POLLIN` when the count is nonzero. The producer wakes every 250 ms, increments selected file counters up to ten, and notifies any saved poll handle for files that became ready.

## State and Persistence
All state is in process memory: open mask, poll handles, counts, global `struct fuse *`, mutex, stop flag, and producer thread. Counts behave like small pipe buffers. There is no persistence after unmount. Poll handles are single-use references that must be destroyed by the filesystem once no longer needed.

## Dependencies and Integration Points
The file uses high-level libfuse, `fuse_get_context()` to obtain `struct fuse *`, `fuse_notify_poll()`, pthreads, and POSIX `poll` event constants. It is paired with `poll_client.c`, which opens all files and uses `select()`.

## Risks
`fsel_open_mask` is modified without the mutex, so concurrent opens/releases can race. Only one open per file is supported because the file index is used as `fi->fh`; broader use would need open-instance allocation. If a client closes without a later poll replacement, handle lifetime depends on the most recent destroy path. Producer comments say 500 ms but the interval is 250 ms.

## Test Signals
Run `poll` mounted in a directory, run `poll_client` from that mount, and observe readiness/read counts rotating across hex files. Confirm opening the same file twice returns `EBUSY`, writes fail with `EACCES`, reads consume counts, and unmount joins the producer thread cleanly.
