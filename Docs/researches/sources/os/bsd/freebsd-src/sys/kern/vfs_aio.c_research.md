# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_aio.c

## Role

Implements FreeBSD kernel support for POSIX AIO and list I/O. It provides syscall entry points, per-process AIO state, worker kernel processes, completion notification, cancellation, kqueue integration, compatibility ABI handling, and special direct BIO support for character disk devices.

## Main Responsibilities

- Provides `aio_read`, `aio_write`, vectored AIO, `aio_fsync`, `aio_mlock`, `aio_suspend`, `aio_cancel`, `aio_error`, `aio_return`, `aio_waitcomplete`, and `lio_listio`.
- Maintains per-process AIO queues and completion lists.
- Schedules blocking work on `aiod` kernel processes.
- Uses a direct BIO fast path for eligible character disk device I/O.
- Handles fsync ordering relative to earlier queued writes.
- Delivers completion through status fields, signals, and kqueue.
- Provides FreeBSD 6 and 32-bit compatibility shims.

## Global Configuration and State

The file registers `FEATURE(aio)` and a loadable `aio` module. Sysctls under `vfs.aio` control and expose:

- `enable_unsafe`: permit AIO on file types not known safe.
- `unsafe_warningcnt`: warning budget for unsafe attempts.
- `max_aio_procs`, `num_aio_procs`, `target_aio_procs`.
- `max_aio_queue`, `num_queue_count`.
- `num_buf_aio`, `num_unmapped_aio`.
- `aiod_lifetime`.
- `max_aio_per_proc`.
- `max_aio_queue_per_proc`.
- `max_buf_aio`.

POSIX config values are exported through `_p1003_1b`, including `aio_listio_max`.

## Key Data Structures

- `struct kaiocb`: kernel AIO control block for one request.
- `struct kaioinfo`: per-process AIO state, queues, counters, mutex, and scheduling tasks.
- `struct aioliojob`: aggregate state for `lio_listio()`.
- `struct aioproc`: bookkeeping for an AIO worker process.
- `struct aiocb_ops`: ABI-specific operations for copying aiocbs in/out and updating user-visible status/error fields.

Important queues:

- `kaio_all`: all process AIO jobs.
- `kaio_done`: completed jobs awaiting `aio_return()` or `aio_waitcomplete()`.
- `kaio_jobqueue`: queued/running jobs.
- `kaio_syncqueue`: fsync jobs waiting on previous I/O.
- `kaio_syncready`: fsync jobs ready to schedule.
- global `aio_jobs`: jobs available to worker daemons.
- global `aio_freeproc`: idle worker daemons.

## Initialization and Worker Pool

`aio_onceonly()` registers exit/exec rundown handlers, kqueue filters, UMA zones, global locks, and POSIX feature config.

`aio_init_aioinfo()` creates per-process AIO state lazily and starts enough worker daemons to approach `target_aio_procs`.

`aio_daemon()` is the worker loop:

- Selects runnable jobs from the global queue.
- Switches vmspace to the user process for user-buffer I/O.
- Runs the job’s handler.
- Tracks per-process active job limits.
- Returns to its own vmspace before sleeping.
- Exits after `aiod_lifetime` if there are more workers than target.

`aio_newproc()` creates new `aiod%d` kernel processes and waits until each has started.

## Request Queueing

`aio_aqueue()` is the central queueing path:

- Initializes per-process AIO state if needed.
- Stores initial user status/error.
- Enforces global and per-process queue limits.
- Copies in the aiocb through ABI-specific `aiocb_ops`.
- Validates size, opcode, signal/kqueue notification, fd rights, offsets, and path-file exclusions.
- Fetches the file object using appropriate Capsicum rights:
  - reads use `cap_pread_rights`,
  - writes use `cap_pwrite_rights`,
  - sync uses `cap_fsync_rights`,
  - no-op uses `cap_no_rights`.
- Sets up `uio` for scalar or vectored I/O.
- Uses file-specific `fo_aio_queue` if present, otherwise `aio_queue_file()`.
- Inserts successful jobs into per-process tracking queues.

`LIO_NOP` requests are validated and then discarded without queueing.

## File Backend and Safety Policy

`aio_queue_file()` first tries `aio_qbio()` for fast disk-device I/O. If that is not eligible, it only permits generic threaded AIO by default for local regular files and directories. Other file types require `vfs.aio.enable_unsafe=1`; otherwise the request fails with `EOPNOTSUPP` and can log a counted warning.

Generic jobs are scheduled to worker daemons:

- read/write: `aio_process_rw()`
- sync/dsync: `aio_process_sync()`
- mlock: `aio_process_mlock()`

Fsync jobs are ordered after earlier queued read/write jobs on the same file. Earlier jobs receive `KAIOCB_CHECKSYNC`; when they complete, dependent sync jobs are moved from `kaio_syncqueue` to `kaio_syncready`.

## Direct BIO Fast Path

`aio_qbio()` supports high-performance AIO for eligible `VCHR` disk devices:

- Requires vnode file type and character-device vnode.
- Requires block-size alignment and `iovcnt <= max_buf_aio`.
- Requires disk device flags and `si_iosize_max` compliance.
- Pins user pages with `vm_fault_quick_hold_pages()`.
- Uses mapped `pbuf` buffers or unmapped BIOs depending on device flags and `unmapped_buf_allowed`.
- Submits one BIO per iovec through `d_strategy`.
- Completes through `aio_biowakeup()` when all BIOs finish.

`aio_biocleanup()` unmaps/unholds pages, frees BIO resources, updates counters, and releases per-process buffer accounting.

## Completion and Notification

`aio_complete()` sets final status/error and, if queueing/cancellation is not deferring it, removes the job from the job queue and calls `aio_bio_done_notify()`.

`aio_bio_done_notify()`:

- Moves jobs to `kaio_done`.
- Updates list-I/O finished counts.
- Sends per-job signal notifications.
- Triggers per-job kqueue notes.
- Sends or posts LIO aggregate notifications when all list jobs finish.
- Wakes waiters sleeping in suspend/waitcomplete/rundown paths.
- Schedules dependent fsync jobs once prerequisites complete.

`aio_return()` and `aio_waitcomplete()` both free kernel job resources as a side effect after returning status to the caller.

## Cancellation and Rundown

Cancellation is cooperative and backend-aware:

- `aio_set_cancel_function()` installs a backend cancel routine.
- `aio_clear_cancel_function()` prevents races when a job is selected for execution.
- `aio_cancel_job()` marks a job cancelled and invokes its cancel callback if available.
- `aio_cancel_daemon_job()` removes generic daemon jobs from the global queue and completes with `ECANCELED`.
- `aio_cancel_sync()` removes pending sync jobs from `kaio_syncqueue`.

`sys_aio_cancel()` uses a marker job to safely walk the queue while dropping locks during cancellation.

`aio_proc_rundown()` runs on process exit or exec:

- Marks process AIO state as rundown.
- Cancels pending jobs.
- Waits for running jobs.
- Frees completed jobs and empty LIO jobs.
- Drains taskqueue tasks.
- Destroys per-process AIO state.

## Syscall Surface

Primary native syscalls include:

- `sys_aio_read()`, `sys_aio_readv()`
- `sys_aio_write()`, `sys_aio_writev()`
- `sys_aio_mlock()`
- `sys_aio_fsync()`
- `sys_lio_listio()`
- `sys_aio_return()`
- `sys_aio_suspend()`
- `sys_aio_cancel()`
- `sys_aio_error()`
- `sys_aio_waitcomplete()`

Shared helpers implement most behavior:

- `kern_aio_return()`
- `kern_aio_suspend()`
- `kern_aio_error()`
- `kern_aio_waitcomplete()`
- `kern_aio_fsync()`
- `kern_lio_listio()`

## Kqueue Integration

The file registers filters:

- `EVFILT_AIO`
- `EVFILT_LIO`

Attach functions require kernel-created registrations using `EV_FLAG1`, because userland must not supply raw kernel job pointers. Completion sets `EV_EOF` for AIO jobs; LIO readiness is based on `LIOJ_KEVENT_POSTED`.

## ABI Compatibility

The file includes two compatibility layers:

- `COMPAT_FREEBSD6`: supports older `osigevent` layout and old aiocb structures.
- `COMPAT_FREEBSD32`: translates 32-bit aiocb, iovec, signal event, timeout, and pointer layouts.

`struct aiocb_ops` lets native, old, and 32-bit ABIs share the same kernel queueing/completion implementation.

## Research Relevance

This file is important for filesystem and storage research because it is the kernel path connecting POSIX AIO to VFS file operations, vnode fsync, direct GEOM/BIO disk I/O, user-page pinning, and per-process resource governance. It also shows how FreeBSD handles async completion semantics across signals, kqueue, process exit, exec, cancellation, and ABI compatibility.
