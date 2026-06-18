# sources/test-tools/ior/src/aiori-aio.c

## Purpose
Provides an IOR backend named `AIO` that layers Linux native asynchronous I/O (`libaio`) over the existing POSIX backend. It batches transfers, keeps a pool of aligned buffers for asynchronous operations, and delegates filesystem metadata operations to POSIX helpers.

## Important APIs, Types, And Functions
Defines `aio_options_t` for POSIX sub-options, libaio context, pending iocbs, in-flight counts, pending bytes, and buffer pool state. Defines `aio_fd_t` wrapping a POSIX fd. Key functions are `aio_options`, `aio_initialize`, `aio_setup_pool`, `submit_pending`, `aio_reap_one`, `process_some`, `complete_all`, `aio_Xfer`, `aio_Close`, `aio_Fsync`, and `aio_Sync`. Registers `aio_aiori`.

## Control Flow
Initialization creates one `io_context_t` and allocates an iocb submission array sized by `granularity`. Open/create delegate to POSIX. For normal reads/writes, `aio_Xfer` ensures capacity, provisions a buffer pool, copies write data into a pooled buffer, prepares a pwrite/pread iocb, queues it, and submits when granularity is reached. When maximum in-flight operations is reached, it reaps some completions. For verification reads, it synchronizes all outstanding work and performs a blocking single AIO so the caller's buffer is immediately valid. Close/fsync/sync call `complete_all` before delegating.

## State And Persistence Behavior
Runtime state is in backend options and is shared by the backend instance: libaio context, in-flight counters, pending-byte accounting, and buffer pool. Data persistence is ordinary POSIX file persistence through the underlying POSIX fd. Read operations into the pool do not copy data back to the caller except in verification paths, so non-check read benchmarking measures completion of async reads without returning useful payload to IOR.

## Dependencies And Integration Points
Depends on `libaio`, POSIX AIORI functions from `aiori-POSIX.h`, aligned buffer utilities, and the IOR backend contract. It forwards xfer hints to POSIX, uses POSIX option parsing through `option_merge`, and reuses POSIX statfs/access/mkdir/rmdir/stat/remove/get_file_size.

## Risks And Edge Cases
`pending_bytes` is incremented for reads as well as writes and decremented by completion result; short I/O or errors are detected only at completion. Non-check reads never copy pooled read data into the caller's buffer, which is acceptable for pure throughput but surprising if a caller expects data. `io_submit` error handling uses `errno`, although libaio often returns negative errno values directly. The stack VLA in `complete_all`/`process_some` is bounded to 512 events but still depends on runtime values. `aio_check_params` enforces minimum max-pending and granularity constraints but not zero/negative granularity explicitly.

## Test Signals
Exercise AIO with write/read and write-check/read-check modes, direct/aligned POSIX options, `aio.max-pending` and `aio.granularity` boundary values, short file reads, fsync-per-write, and close/sync completion. Error injection for `io_submit`/`io_getevents` would validate pending-byte accounting and abort paths.
