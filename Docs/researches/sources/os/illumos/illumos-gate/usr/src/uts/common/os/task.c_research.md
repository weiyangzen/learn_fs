# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/task.c

## Purpose

Implements illumos kernel task objects: process groupings associated with projects and zones for resource accounting, resource controls, signal/administrative targeting, processor binding, fair-share scheduling integration, and extended accounting commit.

A task is a collection of processes with a common project ID and common initial parent lineage. The code manages task identity, membership, lifetime, resource-control state, per-task usage accounting, kstats, and final extended-accounting commit.

## Main Responsibilities

- Maintain a global task ID namespace and ID-to-task hash.
- Create, hold, release, attach, detach, change, and destroy `task_t` objects.
- Track per-task process count, LWP count, CPU time, and usage snapshots.
- Register task resource controls:
  - `task.max-lwps`
  - `task.max-processes`
  - `task.max-cpu-time`
- Integrate task/project changes with credentials, FSS scheduler state, zones, and resource-control callbacks.
- Initialize primordial `task0` and attach `p0`.
- Publish per-task `nprocs` kstats.
- Commit completed task accounting asynchronously through `exacct_queue`, with a backup commit thread when taskq dispatch fails.

## Locking and Lifetime Model

- `task_hash_lock` protects the global task hash and ID lookup.
- `tk_hold_count` is atomically updated for members and observers.
- Task membership list fields `tk_memb_list`, `p_tasknext`, and `p_taskprev` are protected by `pidlock`.
- A process’s `p_task` is read under `pidlock` or `p_lock` and changed with both.
- `tk_usage_lock` protects task usage structures.
- `tk_cpu_time_lock` protects tick-to-second CPU accounting.
- `zone_nlwps_lock` protects `tk_nlwps`, `tk_nprocs`, project task counts, and related task/project limits.
- Task teardown removes the task from the hash before committing accounting, so no new observer can find it.

## Key Entry Points

- `task_hold_by_id_zone()` / `task_hold_by_id()`
  Find a task by ID with zone visibility checks and return it held.

- `task_hold()` / `task_rele()`
  Manage task references. The final release removes the task from the hash, updates project task counts, deletes kstats, and dispatches extended-accounting commit.

- `task_create()`
  Allocates a new task, assigns an ID, holds the destination project and zone, duplicates ancestor resource controls, records ancestor task ID, inserts into the hash, and creates kstats.

- `task_attach()`
  Inserts a process into the task’s circular membership list and sets `p_task`.

- `task_begin()`
  Initializes start time and attaches the first member, then runs resource-control duplicate callbacks once process-to-task linkage exists.

- `task_detach()`
  Removes a process from its task membership list, tears off observational rctls from task/project rctl sets, and clears process task links.

- `task_change()`
  Moves a process between tasks, adjusting LWP/process counters and extended-accounting microstate ownership.

- `task_join()`
  Moves `curproc` into a new task during `settaskid()`-style operations. It updates credentials for project ID, allocates FSS buffers, changes task membership, updates all threads’ project pointers, and optionally marks the new task final.

- `task_end()`
  Final frees after accounting commit: releases project and zone holds, frees usage and inherited usage buffers, frees rctl set, returns task ID, and frees the task cache object.

- `task_cpu_time_incr()`
  Called by clock accounting to convert accumulated CPU ticks into task CPU seconds.

- `task_init()`
  Initializes caches, ID space, task hash, rctls, primordial `task0`, and p0 task membership.

- `task_commit_thread_init()` / `task_commit()`
  Starts and runs the backup commit thread used if `taskq_dispatch(exacct_queue, ...)` fails during final release.

## Resource Control Behavior

- `task_lwps_usage()` / `task_lwps_test()` / `task_lwps_set()` expose and enforce task LWP limits.
- `task_nprocs_usage()` / `task_nprocs_test()` / `task_nprocs_set()` expose and enforce task process limits.
- `task_cpu_time_usage()` / `task_cpu_time_test()` expose CPU-time usage and threshold testing; CPU-time rctl is configured as non-denying, CPU-time, infinite-capable, seconds-based, and unobservable.

## Filesystem Relevance

This is not filesystem code, but it is part of the OS resource-control and accounting substrate used by filesystem-facing workloads. Filesystem daemons, kernel service processes, zones, and user processes doing file I/O are accounted and limited through tasks/projects. Extended accounting can include file-service workload attribution, and kernel task queues are used to commit task accounting records.

## Notable Edge Cases

- `task_rele()` may be called with `pidlock` held, so final accounting dispatch uses `TQ_NOSLEEP | TQ_NOQUEUE` and falls back to a dedicated commit list/thread.
- `task_create()` duplicates ancestor task rctls without callbacks first because the process-to-new-task linkage is not established yet.
- `task_join()` must operate on a stopped or effectively single-threaded process and returns with `p_lock` held.
- Thread project changes wake waiting threads and clear `TS_PROJWAITQ` so they do not remain on an obsolete project wait queue.
- Final `task_end()` must not reference any process; membership is already gone.
