# File Research: sources/os/linux/linux/io_uring/sqpoll.c

Submission-queue polling implementation. This file creates, attaches, parks, runs, and tears down kernel SQPOLL threads that submit SQEs on behalf of userspace.

Key responsibilities:
- Manages `io_sq_data` lifetime, references, park/unpark, stop, and finish.
- Supports attaching a ring to an existing SQPOLL worker from the same thread group.
- Runs the SQPOLL thread loop, including SQ submission, iopoll harvesting, task_work execution, NAPI busy polling, idle sleep, and wakeup flag management.
- Creates SQPOLL offload during ring setup, including security checks and optional CPU affinity.
- Provides SQ full wait helper and SQPOLL io-wq CPU affinity update.

Important data flows:
- `io_sq_offload_create()` creates or attaches `io_sq_data`, links the ctx while the thread is parked, starts a new io thread if needed, and allocates the thread's io_uring task context.
- The SQ thread iterates attached contexts, caps submission count when serving multiple rings, overrides credentials to ring submitter creds, submits SQEs, reaps iopoll, and wakes submitters waiting for SQ space.
- When idle, the thread sets `IORING_SQ_NEED_WAKEUP`, checks for SQ entries with a memory barrier, then sleeps on `sqd->wait`.
- Stop path cancels outstanding work, marks rings as needing wakeup, runs final task_work, and completes `sqd->exited`.

Concurrency and locking:
- `sqd->lock` protects attached ctx list, thread pointer, park state, and SQPOLL coordination.
- Park/unpark uses `park_pending` and state bits so nested park requests are honored.
- Thread pointer is RCU-published and protected by `sqd->lock`.

Important invariants:
- `IORING_SETUP_ATTACH_WQ` without SQPOLL is validated for compatibility and rejected.
- Attached SQPOLL workers must belong to the same thread group.
- SQ affinity requires SQPOLL and an online CPU allowed by cpuset.
- The SQ thread must not attach to a dying worker.
