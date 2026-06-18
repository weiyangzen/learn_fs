# sources/test-tools/fio/engines/posixaio.c

## Purpose
Implements fio's POSIX AIO engine using `aio_read()`, `aio_write()`, `aio_suspend()`, `aio_error()`, `aio_return()`, and optionally `aio_fsync()`. It is a portable async engine relative to Linux native AIO, with synchronous fallbacks for trim and some sync paths.

## Important APIs, Types, And Functions
`struct posixaio_data` stores completed event pointers and current queued count. Important functions are `fio_posixaio_init()`, `fio_posixaio_prep()`, `fio_posixaio_queue()`, `fio_posixaio_getevents()`, `fio_posixaio_event()`, and `fio_posixaio_cleanup()`.

## Control Flow
`prep` fills the per-`io_u` `aiocb` with file descriptor, buffer, length, offset, and `SIGEV_NONE`, then clears `io_u->seen`. `queue` issues `aio_read()` or `aio_write()`, handles trim synchronously only when no POSIX AIO is queued, and either calls `aio_fsync()` for sync directions or falls back to fio synchronous sync when unavailable. `EAGAIN` maps to `FIO_Q_BUSY` so fio naturally throttles queue depth. `getevents` scans all in-flight `io_u`s, calls `aio_error()`, records completions, computes residuals with `aio_return()`, waits on up to eight active aiocbs with `aio_suspend()`, and respects an approximate timeout using monotonic time.

## State And Persistence
State is per-thread: queued count and a completion array sized by `iodepth`. The POSIX AIO control block itself is embedded in each `io_u`. Persistent effects are normal file reads/writes and optional fsync.

## Dependencies And Integration Points
Depends on POSIX AIO, fio generic file helpers, fio `io_u_all` iteration, and optional `CONFIG_POSIXAIO_FSYNC`. The registered engine flags advertise asynchronous trim/syncfs handling behavior.

## Risks
`aio_suspend()` is called even if `suspend_entries` is zero after scans, depending on workload state. Timeout handling restarts scans and can be approximate. `retval` from `aio_return()` is used directly to compute residual; negative unexpected returns could inflate residual. Completion scanning is O(total io_u) per getevents call.

## Test Signals
Test reads/writes at varying queue depths, low OS AIO limit producing `EAGAIN`, trim while queued vs idle, fsync with and without `CONFIG_POSIXAIO_FSYNC`, cancellations (`ECANCELED`), timeout behavior, residual computation for short I/O, and cleanup.
