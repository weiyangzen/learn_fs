# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/taskq.c

## Purpose

Implements illumos kernel task queues: a general-purpose asynchronous execution facility for deferring work to kernel threads. It supports traditional FIFO task queues, dynamic bucketed task queues with per-task worker threads, global `system_taskq`, CPU-percentage thread-count adjustment, suspend/resume, CPR integration, kstats, debug fault injection, and taskq lifetime management.

## Main Responsibilities

- Initialize taskq and taskq-entry caches.
- Create and destroy static and dynamic task queues.
- Dispatch work with normal allocation, no-sleep allocation, no-allocation, front insertion, no-backlog, and preallocated-entry variants.
- Maintain worker threads for fixed/static queues.
- Maintain dynamic taskq workers distributed across hash buckets plus a shared idle bucket.
- Provide backlog queues when dynamic taskqs are resource constrained.
- Grow dynamic buckets on demand and redistribute worker threads to buckets that have backlog but no workers.
- Support taskq suspension, resumption, waiting, empty checks, and membership checks.
- Adjust thread counts for `TASKQ_THREADS_CPU_PCT` queues when CPUs or processor sets change.
- Publish kstats for static and dynamic queues.

## Queue Types

### Static Task Queues

Static task queues use:

- A single circular doubly linked `tq_task` queue.
- A `tq_freelist` of reusable `taskq_ent_t` objects.
- One or more long-lived worker threads running `taskq_thread()`.
- FIFO execution when `nthreads == 1`; otherwise order is not guaranteed.
- `tq_threadlock` reader/writer synchronization to suspend execution.

Important paths:

- `taskq_dispatch()` allocates a task entry and enqueues it with `TQ_ENQUEUE()` or `TQ_ENQUEUE_FRONT()`.
- `taskq_dispatch_ent()` enqueues caller-provided preallocated entries and never frees them.
- `taskq_thread()` manages thread creation/exit, executes queued work, records runtime stats, and frees or preserves entries depending on preallocation.

### Dynamic Task Queues

Dynamic task queues use:

- `tq_buckets[0..tq_nbuckets-1]` for hashed work distribution.
- One extra idle bucket at `tq_buckets[tq_nbuckets]`.
- Per-bucket freelists of idle worker-backed entries.
- Per-bucket backlog lists for deferred work without an available worker.
- One ordinary backing taskq thread used only for overflow/extension jobs.
- Worker threads running `taskq_d_thread()` and servicing buckets through `taskq_d_svc_bucket()`.

Dispatch flow:

1. Hash `arg` and current CPU hint with `TQ_HASH()` to select a bucket.
2. Try `taskq_bucket_dispatch()` on the selected bucket.
3. Try `taskq_idlebucket_dispatch()` to move an idle worker to the selected bucket.
4. For sleepable dispatches, call `taskq_bucket_extend()` to create a worker and retry.
5. If allowed, enqueue the job on the bucket backlog.
6. Schedule `taskq_bucket_overflow()` on the backing queue to try extension or redistribution.

Dynamic task queues do not support `TQ_NOALLOC` or `TQ_FRONT` in public dispatch assertions. `TQ_NOQUEUE` prevents backlog use and is important for dependent tasks that could deadlock if queued behind each other.

## Key Entry Points

- `taskq_init()`
  Creates `taskq_ent_cache`, `taskq_cache`, the instance ID arena, and the CPU-percentage taskq list.

- `taskq_mp_init()`
  Registers CPU setup callbacks and synchronizes CPU-percentage queues after MP startup.

- `system_taskq_init()`
  Creates global dynamic `system_taskq`.

- `taskq_create()`, `taskq_create_instance()`, `taskq_create_proc()`, `taskq_create_sysdc()`
  Public constructors for kernel task queues, with optional instance IDs, target process, and system duty cycle scheduling.

- `taskq_create_common()`
  Shared constructor. It validates incompatible flags, computes bucket/thread limits, canonicalizes the name, prepopulates entries when requested, holds the taskq process’s zone, starts static backing thread(s), initializes dynamic buckets and idle workers, allocates instance IDs, and installs kstats.

- `taskq_destroy()`
  Deletes kstats, unregisters CPU-percentage queues, waits for queued/running work, stops static backing threads, frees cached entries, closes and drains dynamic buckets, waits for dynamic worker exit, releases the zone hold, and frees the taskq object.

- `taskq_dispatch()`
  Main public dispatch routine for both static and dynamic task queues.

- `taskq_wait()` / `taskq_wait_id()`
  Wait until all already queued/running work has completed. For dynamic queues it also waits for per-bucket allocation and backlog counts to drain.

- `taskq_suspend()` / `taskq_resume()` / `taskq_suspended()`
  Suspend and resume execution. Static queues block workers through `tq_threadlock`; dynamic queues mark buckets suspended so new dispatches fail or backlog.

- `taskq_member()`
  Checks `thread->t_taskq`.

## Important Internal Helpers

- `taskq_ent_alloc()` / `taskq_ent_free()`
  Manage static taskq entry allocation, freelist reuse, min/max allocation throttling, and max-allocation wait signaling.

- `taskq_ent_exists()`
  Checks whether a backing queue already has a specific `func(arg)` entry, used to avoid duplicate overflow extension jobs.

- `taskq_thread_create()`
  Creates static/backing taskq threads, including LWP-backed or duty-cycle threads when requested, and waits during initial creation until enough threads can service requests.

- `taskq_thread_wait()`
  Common wait helper with CPR-safe handling.

- `taskq_backlog_dispatch()` / `taskq_backlog_enqueue()`
  Allocate and enqueue dynamic backlog entries, update backlog stats, and wake a newly idle bucket worker if one appeared between dispatch attempts.

- `taskq_d_svc_bucket()`
  Dynamic worker bucket loop. It runs assigned work, drains backlog, puts the worker entry on the bucket freelist, waits briefly, and migrates away if idle.

- `taskq_d_thread()`
  Dynamic worker lifecycle. It services buckets, searches for backlog across buckets, migrates to the idle bucket, waits with timeout, exits when surplus/closing, and updates dynamic thread counts.

- `taskq_bucket_extend()`
  Creates a stopped worker thread, links its entry into a bucket freelist, accounts thread creation, and starts the thread. It observes memory pressure and max-thread limits.

- `taskq_bucket_overflow()`
  Asynchronous extension request that tries to create a worker, then redistributes if extension fails.

- `taskq_bucket_redist()`
  Redirects a worker from an over-provisioned donor bucket to a recipient bucket that has backlog and no threads.

- `taskq_kstat_update()` / `taskq_d_kstat_update()`
  Populate static and dynamic taskq kstats.

## Data Structures

- `taskq_t`
  Queue object with locks, dispatch/wait CVs, thread targets, flags, freelists, backing queue, dynamic bucket array, process/zone context, kstats, and counters.

- `taskq_ent_t`
  Work item and/or worker token. Stores list links, function, argument, either bucket pointer or flags, worker thread pointer, and per-entry CV.

- `taskq_bucket_t`
  Dynamic bucket with lock, backlog list, freelist, counts for allocated/free/backlog entries, flags, CV, total runtime, and statistics.

- `tqstat_t`
  Per-bucket statistics for hits, misses, overflow/backlog use, dispatch-triggered creates, thread creates/deaths, maximum thread count, and backlog peak.

## Locking Model

- Bucket locks are ordered before `tq_lock` where both are needed.
- Idle bucket lock precedes hashed bucket locks in documented multi-bucket cases.
- `taskq_cpupct_list` is protected by `cpu_lock`.
- `tq_lock` protects static queue state, thread target changes, allocation counts, and backing queue state.
- `tq_threadlock` gates execution for static queue suspend/resume.
- Dynamic bucket state is protected by each bucket’s `tqbucket_lock`.
- Dynamic per-bucket statistics are intentionally not strongly synchronized.

## Filesystem Relevance

Task queues are core kernel infrastructure used by filesystems, VFS, storage drivers, networking, STREAMS, ZFS-related services, and asynchronous cleanup paths. Filesystem code often needs to defer work out of interrupt, lock-held, or nonblocking contexts; `taskq.c` supplies that mechanism. The dynamic taskq behavior is especially relevant for high-volume storage/filesystem work that needs concurrency without a single global queue bottleneck.

## Notable Edge Cases

- `TASKQ_DYNAMIC`, `TASKQ_CPR_SAFE`, and `TASKQ_THREADS_CPU_PCT` are mutually incompatible.
- `TASKQ_DUTY_CYCLE` and `TASKQ_THREADS_LWP` cannot use `p0` as the taskq process.
- `TASKQ_NOQUEUE` on dynamic dispatch avoids backlog deadlocks for dependent tasks.
- Static taskq max allocation is advisory for sleeping dispatches; it throttles by waiting up to one second rather than blocking indefinitely on task completion.
- Dynamic worker creation is suppressed under low memory unless the target bucket has no workers.
- Dynamic taskq destruction avoids waking every idle-bucket worker at once; idle workers wake each other in sequence.
- Dynamic migration uses sentinel functions `taskq_d_migrate` and `taskq_d_redirect` that should never actually run.
- `taskq_wait()` must not be called from a taskq worker in the same queue.
