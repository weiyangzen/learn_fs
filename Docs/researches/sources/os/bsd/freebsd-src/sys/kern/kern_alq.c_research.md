# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_alq.c

## Purpose
Implements the kernel asynchronous logging queue facility. Producers append fixed or variable sized records to in-memory circular buffers; a kernel daemon drains active queues to vnode-backed log files.

## Key Elements
- Queue type: `struct alq`.
- Entry type used by zero-copy API: `struct ale`.
- Global daemon/list state: `ald_queues`, `ald_active`, `ald_mtx`, `ald_proc`, `ald_thread`.
- Queue flags: `AQ_WANTED`, `AQ_ACTIVE`, `AQ_FLUSHING`, `AQ_SHUTDOWN`, `AQ_ORDERED`, `AQ_LEGACY`.
- Public APIs: `alq_open_flags()`, `alq_open()`, `alq_writen()`, `alq_write()`, `alq_getn()`, `alq_get()`, `alq_post_flags()`, `alq_flush()`, `alq_close()`.
- Module: `DECLARE_MODULE(alq, ...)`.

## Daemon And Shutdown
`ald_startup()` initializes global locks and lists. `ald_daemon()` waits for active queues, removes them from the active list, calls `alq_doio()`, and wakes blocked producers when space becomes available.

`ald_shutdown()` is registered on `shutdown_pre_sync`; it blocks new queues, drains every queue, wakes the daemon, and waits for daemon exit unless `RB_NOSYNC` or scheduler-stopped conditions apply.

## Queue Operation
`alq_open_flags()`:
- Opens/creates the target file for writing with `O_NOFOLLOW`.
- Holds a vnode reference and credential.
- Allocates the `alq` and ring buffer.
- Registers the queue globally unless shutdown is in progress.

`alq_open()` provides legacy fixed-size entry setup when `count > 0`.

`alq_writen()`:
- Checks message size, shutdown state, free space, and `ALQ_NOWAIT`.
- Supports ordered writers via `AQ_ORDERED`.
- Sleeps for resources when allowed.
- Copies data into the circular buffer with wrap handling.
- Activates the queue unless `ALQ_NOACTIVATE` is used.

`alq_getn()` / `alq_post_flags()` provide a direct-write API to avoid a copy. `alq_getn()` may wrap early to preserve contiguous space and records the skipped bytes in `aq_wrapearly`.

## Disk Flush
`alq_doio()`:
- Builds one or two iovecs depending on circular-buffer wrap.
- Performs `VOP_WRITE()` with `IO_UNIT | IO_APPEND`.
- Uses MAC write checks when enabled.
- Updates write tail, free byte count, wrap state, and queue indices.
- Wakes waiters when `AQ_WANTED` was set.

The source explicitly ignores `VOP_WRITE` errors in this path.

## Research Notes
The facility separates producer latency from disk I/O but does not provide per-record durable success reporting. The `ALQ_NOACTIVATE` path is intentionally constrained to avoid deadlocks when pending inactive data would prevent progress.
