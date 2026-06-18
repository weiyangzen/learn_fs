# sources/storage-engines/foundationdb/fdbrpc/libeio/eio.c

## Purpose

`eio.c` is the bundled libeio implementation that gives FoundationDB asynchronous POSIX-style filesystem operations through a detached worker-thread pool. `AsyncFileEIO.h` initializes it, submits open/read/write/fsync/stat/custom requests, and polls completions from the Flow network thread.

## Important APIs, types, and functions

Public API implementations include `eio_init()`, `eio_poll()`, tuning setters, counters, `eio_submit()`, `eio_cancel()`, synchronous working-directory helpers, request wrappers such as `eio_open()`, `eio_read()`, `eio_write()`, `eio_fsync()`, `eio_stat()`, `eio_readdir()`, `eio_custom()`, group functions, and `eio_sendfile_sync()`. Internal subsystems include priority queues `req_queue` and `res_queue`, worker management through `etp_proc()`, `etp_start_thread()`, and `etp_maybe_start_thread()`, execution dispatch in `eio_execute()`, completion in `eio_finish()`, and helper implementations for `sendfile`, `realpath`, `readdir`, `sync_file_range`, `mlock`, `msync`, `fallocate`, and missing POSIX functions.

## Control flow, state, and persistence

`eio_init()` creates mutexes/condition variables and initializes global queues/counters. `eio_submit()` normalizes priority, increments in-flight counters, and either places normal requests on `req_queue` for worker threads or places group requests directly on `res_queue`. Workers in `etp_proc()` wait on `reqwait`, execute requests via `eio_execute()`, record `errno` into `req->errorno`, then push completed requests to `res_queue` and call `want_poll_cb` when the poller should wake. `eio_poll()` drains completed requests, decrements counters, invokes finish callbacks unless cancelled, destroys request-owned buffers, and enforces optional max-time/max-request budgets. Group requests track child counts, optional feed callbacks, cancellation propagation, and delayed group completion while children remain. State is global process memory: thread counts, idle limits, queues, locks, callbacks, and per-worker temporary buffers.

## Dependencies and integration points

The file includes platform config headers, `eio.h`, `ecb.h`, and `xthread.h`. It uses pthreads or Windows pthread wrappers, POSIX file APIs, `openat`/`*at` APIs when available, platform `sendfile`, `mmap` synchronization, and Linux syscalls where configured. In FoundationDB, CMake builds it as static library `eio` on non-Windows when no system `eio` is used, with warnings disabled and `USE_UCONTEXT` defined. `AsyncFileEIO` calls `eio_set_max_parallel()`, `eio_init()`, `eio_poll()`, wrappers, and `eio_custom()` for platform-specific fsync work.

## Risks and test signals

The implementation uses global state and is intended to be initialized once. Cancellation is cooperative: it sets `cancelled`, short-circuits queued execution, and can interrupt long `readdir`/`mtouch` loops, but it cannot stop arbitrary blocking syscalls already running. Worker shutdown uses sentinel requests and detached threads. Some emulations, especially `pread`/`pwrite` via `lseek`, `sendfile` fallback, and `realpath`, have race or performance caveats. In `eio__mtouch()`, the page-walk loop compares the absolute address against `len` rather than the computed end, which looks suspicious for multi-page ranges. Test signals include `AsyncFileEIO` open/read/write/truncate/fsync/stat tests, cancellation-on-future-error paths, high concurrency with `FLOW_KNOBS->EIO_MAX_PARALLELISM`, parent-directory fsync/custom requests, and thread sanitizer or stress tests around queue counters.
