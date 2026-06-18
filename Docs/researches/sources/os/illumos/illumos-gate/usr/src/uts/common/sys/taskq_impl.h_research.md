# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/taskq_impl.h

## Purpose
Defines private taskq implementation structures, statistics, bucket state, internal flags, and preallocated dispatch support.

## Main Interfaces
- `taskq_ent_t`: queued task entry with list links, function, argument, bucket/flags union, executing thread, and completion CV.
- `TQENT_FLAG_PREALLOC`.
- `tqstat_t`: unlocked per-bucket statistics for hits, misses, dispatch-created tasks, overflow, backlog, thread creates/deaths, and max threads.
- `taskq_bucket_t`: per-CPU bucket with lock, enclosing taskq, backlog/freelist heads, allocation/backlog/free counts, CV, flags, total time, and stats.
- Bucket flags:
  - `TQBUCKET_CLOSE`
  - `TQBUCKET_SUSPEND`
  - `TQBUCKET_REDIRECT`
- Implementation taskq flags:
  - `TASKQ_CHANGING`
  - `TASKQ_SUSPENDED`
  - `TASKQ_NOINSTANCE`
  - `TASKQ_THREAD_CREATED`
  - `TASKQ_DUTY_CYCLE`
- `struct taskq`: full taskq state including locks/CVs, priority, flags, thread counts/limits, freelist, bucket array, instance, thread pointer/list, CPU percentage linkage, process/cpupart/SDC duty cycle, kstats, timing, counters, and dynamic-thread count.
- `taskq_dispatch_ent()`: special dispatch using caller-provided preallocated entries.
- `TASKQ_THREADS_PCT()`.

## Dependencies And Relationships
Includes taskq, integer, vmem, list, kstat, and rwlock headers. Used only by taskq implementation and tightly coupled to kernel threads, per-CPU buckets, kstats, and optional SDC behavior.

## Research Notes
The header documents that statistics are not lock-protected. Bucket distribution and preallocated entries are central to avoiding allocation in constrained dispatch paths.
