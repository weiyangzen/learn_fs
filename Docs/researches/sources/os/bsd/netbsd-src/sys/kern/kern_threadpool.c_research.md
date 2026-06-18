# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_threadpool.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_threadpool.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements NetBSD kernel thread pools: shared unbound pools and shared per-CPU pools keyed by priority.

## Purpose And Main Interfaces

- Provides reusable kernel worker threads so scheduling a job avoids allocation/sleep in the common path.
- Public pool lifecycle:
  - `threadpools_init`
  - `threadpool_get`
  - `threadpool_put`
  - `threadpool_percpu_get`
  - `threadpool_percpu_put`
  - `threadpool_percpu_ref`
  - `threadpool_percpu_ref_remote`
- Public job lifecycle and control:
  - `threadpool_job_init`
  - `threadpool_job_destroy`
  - `threadpool_schedule_job`
  - `threadpool_cancel_job_async`
  - `threadpool_cancel_job`
  - `threadpool_job_done`

## Key Data Structures

- `struct threadpool` owns:
  - `tp_lock`
  - one dispatcher pseudo-thread record
  - queued jobs
  - idle worker thread list
  - pool refcount
  - dying flag
  - optional bound CPU
  - priority
- `struct threadpool_thread` tracks an LWP, saved LWP name, assigned pool, assigned job, condition variable, and idle-list entry.
- `struct threadpool_unbound` wraps an unbound pool with a global reference count.
- `struct threadpool_percpu` wraps a `percpu_t` containing one `struct threadpool *` per CPU.
- `struct threadpool_job` fields are initialized here but defined externally; jobs carry a callback, interlock, refcount, condition variable, running thread pointer, and display name.

## Control Flow

- `threadpool_get` looks up an unbound pool by priority, creates one outside `threadpools_lock` if absent, then handles races by destroying unused duplicate pools.
- `threadpool_percpu_get` similarly creates a per-CPU pool collection and verifies each CPU initialized successfully.
- `threadpool_create` initializes pool state and creates a dispatcher kthread bound to the requested CPU if applicable.
- `threadpool_schedule_job` requires the caller to hold the job lock. If the job is already running or assigned, scheduling is ignored. Otherwise it takes a job reference and assigns either an idle worker or the dispatcher.
- The dispatcher waits for queued jobs. If no idle workers exist, it creates a worker. If workers exist, it transfers the queued job to one.
- Worker threads wait for assigned jobs, temporarily rename their LWP to the job name, run the job function, require the job to call `threadpool_job_done`, then return to the idle list.
- Idle workers exit after `kern.threadpool.idle_ms` without work, or when the pool is dying.
- `threadpool_destroy` marks the pool dying, wakes dispatcher/workers, and waits for pool refcount to reach zero.

## Concurrency And Invariants

- Global pool registries are protected by `threadpools_lock`.
- Per-pool queues and thread state are protected by `tp_lock`.
- Job completion/cancellation is synchronized through the caller-provided `job_lock`.
- Job refcounts prevent destruction while dispatcher or workers temporarily drop locks.
- Workers assert that jobs call `threadpool_job_done`; otherwise the LWP name is not restored and the assertion fires.
- Remote per-CPU references disable preemption around `percpu_getptr_remote`.

## Risks And Edge Cases

- `threadpool_cancel_job_async` can conservatively fail when the caller passes a different pool than the dispatcher-assigned pool; the code documents this safe false-negative behavior.
- Dispatcher thread creation failure sleeps and retries, leaving queued jobs pending.
- Pool destruction requires no queued jobs and waits for dispatcher/workers to exit.
- Priority validation only accepts `PRI_NONE` or priorities in `[PRI_USER, PRI_COUNT)`.
