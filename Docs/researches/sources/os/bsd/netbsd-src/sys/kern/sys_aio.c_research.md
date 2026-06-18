# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_aio.c

Read completely: 2260 lines.

This file implements NetBSD POSIX asynchronous I/O as a loadable kernel module. Each process gets an AIO service pool with worker threads, a pending job queue, an active/free worker list, a hash table mapping user `aiocb` pointers to kernel jobs, and optional list-I/O request tracking.

Global setup:
- `aio_syscalls` registers `aio_cancel`, `aio_error`, `aio_fsync`, `aio_read`, `aio_return`, `aio_suspend`, `aio_write`, and `lio_listio`.
- `aio_init` initializes job and list-I/O pools, establishes an exit hook, and registers syscalls.
- `aio_fini` removes syscalls and refuses unload while processes still have AIO state.
- sysctls expose `_POSIX_ASYNCHRONOUS_IO`, `aio_listio_max`, and `aio_max`.

Per-process/service-pool flow:
- `aio_procinit` allocates `aioproc`, initializes `aiosp`, creates the aiocb hash, and installs it in `p->p_aio`.
- `aio_exit` destroys hash, workers, mutexes, and process state.
- `aiosp_initialize` initializes queues and the file-group RB tree.
- `aiosp_worker_extract` reuses a free worker or creates one.
- `aiost_create` creates a kernel thread for service work.
- `aiost_entry` waits for assigned work, processes singleton jobs or regular-file groups, returns itself to the freelist, or exits on termination.
- `aiosp_destroy` terminates all free/active workers.

Job behavior:
- `aio_enqueue_job` copies in a user `aiocb`, validates signals/buffer/opcode, initializes per-process state if needed, marks the user aiocb WIP, allocates an `aio_job`, holds the target file, inserts the user-pointer hash handle, checks global/per-process limits, and queues the job.
- `aiosp_distribute_jobs` assigns queued jobs to workers. Regular vnode files are grouped by `file *` through an RB tree; other files get singleton workers.
- `aiost_process_singleton` calls read/write/sync handlers and then marks completion.
- `aio_job_mark_complete` sets `completed`, releases the held file, flushes waitgroups, and sends requested async signals.
- `aiosp_suspend` attaches a waitgroup to selected jobs and waits for any/all completion.
- `aio_cancel`, `aio_error`, and `aio_return` operate through the aiocb hash and job locks.

I/O implementation: `io_read` and `io_write` currently delegate to synchronous fallback implementations on service threads. The fallback builds a single-iovec `uio`, checks file access flags, invokes `fo_read`/`fo_write` with `FOF_UPDATE_OFFSET`, and records retval/errno/state in the kernel job. `io_sync` locks a vnode and calls `VOP_FSYNC`, honoring data-only sync for `AIO_DSYNC`.

Integration: this code sits at the syscall, filedesc, vnode, signal, kthread, pool, and sysctl layers. It is explicitly structured for future nonblocking regular-file optimization, but the current implementation is thread-backed blocking I/O.

Reliability notes: lifecycle and locking are complex: jobs can be queued, active in singleton workers, active inside file-group queues, completed but awaiting `aio_return`, or canceled before distribution. The code validates duplicate active user `aiocb` pointers, but hash insertion can replace an existing mapping. Cancellation only cancels jobs still on the pending service queue, not work already being processed. Limit counters and list-I/O refcounts are sensitive areas for leaks or imbalance on error paths.
