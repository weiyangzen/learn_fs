# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lwp.c

## Purpose

Implements illumos kernel support for lightweight processes: LWP creation, exit, fork duplication, process-wide LWP hold/continue/exit coordination, LWP directory/hash-table maintenance, and per-LWP accounting updates.

This file is central to process/thread lifecycle correctness. It ties together scheduler classes, `/proc` synchronization, zones/tasks/projects resource controls, brand hooks, contract templates, microstate accounting, lgroup placement, and LWP id lookup.

## Main Responsibilities

- Create kernel and user LWPs through `lwp_kernel_create()` and `lwp_create()`.
- Manage LWP stacks, including segkp stack allocation and death-row reuse.
- Enforce task/project/zone `max-lwps` resource controls.
- Grow and maintain `p_lwpdir` and `p_tidhash`.
- Stop, continue, and hold LWPs for fork, fork1, vfork, watchpoints, `/proc`, core dump, exec, and process exit.
- Tear down an exiting LWP and maintain process counts.
- Duplicate LWP state for fork through `forklwp()`.
- Provide fast LWP id lookup and locked lookup for unparking paths.
- Update selected per-LWP resource counters.

## Key Entry Points

- `lwp_kernel_create(proc_t *p, void (*proc)(), void *arg, int state, pri_t pri)`
  Creates a kernel LWP in a system process and returns the backing `kthread_t`.

- `lwp_create(...)`
  Allocates/initializes `klwp_t` and `kthread_t`, assigns tid, links into process thread list, inserts directory/hash entries, performs class/brand/lgroup setup, and optionally starts the LWP.

- `lwp_create_done(kthread_t *t)`
  Completes creation by setting `TS_CREATE | TS_CSTART`, updating `p_lwprcnt`, and making the thread runnable.

- `lwp_exit(void)`
  Main per-LWP exit path. Handles tsd, CPC, poll, doors, schedctl, upimutex, brand exit, `/proc`, zombie/detached LWP handling, counts, scheduler exit, context exit, address-space/HAT transition, and zombie switch.

- `lwp_cleanup(void)`
  Shared cleanup for exiting LWP or process exit, including timers, `/proc` agent cleanup, lgroup removal, and contract template clearing.

- `lwp_suspend(kthread_t *t)` / `lwp_continue(kthread_t *t)`
  Implements targeted LWP suspension and resumption through `TP_HOLDLWP`, `p_holdlwps`, and scheduler state.

- `holdlwp()`, `holdlwps(int holdflag)`, `holdwatch()`
  Process-wide LWP quiescing mechanisms for fork/fork1/watchpoint activity.

- `pokelwps(proc_t *p)`, `runlwps(proc_t *p, ushort_t schedbits)`, `continuelwps(proc_t *p)`
  Force LWPs into kernel, run stopped LWPs, or continue suspended LWPs.

- `exitlwps(int coredump)`
  Coordinates termination or core-dump quiescence of all other LWPs in the process.

- `forklwp(klwp_t *lwp, proc_t *cp, id_t lwpid)`
  Duplicates an LWP into a child process, copying register/FPU/door/contract/brand/scheduler state.

- `lwp_hash_in()`, `lwp_hash_out()`, `lwp_hash_lookup()`, `lwp_hash_lookup_and_lock()`
  Maintain and query process-local LWP id directory/hash structures.

- `lwp_stat_update(lwp_stat_id_t id, long inc)`
  Updates selected `lwp_ru` resource counters.

## Important Data Structures

- `proc_t`
  Uses `p_lock`, `p_tlist`, `p_lwpcnt`, `p_lwprcnt`, `p_lwpdaemon`, `p_lwpwait`, `p_lwpdwait`, `p_lwpdir`, `p_lwpfree`, `p_tidhash`, `p_ret_tidhash`, flags such as `SEXITLWPS`, `SHOLDFORK`, `SHOLDFORK1`, `SHOLDWATCH`, `SWATCHOK`, `SLWPWRAP`.

- `klwp_t`
  Per-LWP kernel state: thread pointer, process pointer, signal alt stack, child stack size, contracts, signal info, brand data, registers/FPU pointers, resource usage.

- `kthread_t`
  Scheduler/thread state: `t_lwp`, `t_tid`, `t_proc_flag`, `t_schedflag`, class fields, binding/lgroup fields, context ops, stack pointer.

- `lwpent_t`, `lwpdir_t`, `tidhash_t`, `ret_tidhash_t`
  LWP directory and LWP id hash table elements. Retired hash tables are retained for safe lockless-ish lookup races.

## Locking and Synchronization

- `p->p_lock` protects process LWP/thread list state, counts, flags, and directory mutations.
- `p->p_zone->zone_nlwps_lock` protects zone/task/project LWP accounting updates.
- Per-bucket `tidhash_t.th_lock` protects LWP id hash buckets.
- `lwp_hash_lookup_and_lock()` intentionally searches without `p_lock`; table growth uses memory barriers and acquires all old/new bucket locks before publishing a new hash table.
- `/proc` synchronization uses `prbarrier(p)` before manipulating states visible to `/proc`.
- `pidlock` protects global thread linkage and join wakeups during final exit.
- `p_holdlwps` condition variable coordinates process-wide holds, exits, and suspension waits.
- `pool_barrier_enter/exit` interaction is handled around stop points in `lwp_create()`.

## Lifecycle Notes

- `lwp_create()` increments task/project/zone LWP counts before allocation; every allocation/class/brand/tid failure path must unwind these counts.
- Default-size LWP stacks can be reused from `lwp_deathrow`; reused context ops are freed before reuse.
- New LWPs are created stopped with `TP_HOLDLWP` and without `TS_CREATE`, so callers can finish initialization before scheduling.
- `lwp_exit()` can trigger whole-process `proc_exit()` when the last non-daemon LWP exits.
- Non-detached exiting LWPs can remain as zombie directory entries until waited for or detached.
- `exitlwps()` has two modes: coredump quiescence without destruction, and full termination for exec/exit/shutdown paths.

## Error and Edge Handling

- System LWP creation failures panic, because system processes should not exhaust LWP ids.
- LWP id wrap uses `SLWPWRAP` and hash lookup to avoid duplicate live tids.
- If process is exiting while creating a current-process LWP, creation fails.
- `holdlwps()` and `holdwatch()` include precedence logic for exit, fork, fork1, watchpoint activity, job control, and `/proc` stops.
- `exitlwps()` handles stopped dangling LWPs from aborted hold operations and cleans zombie LWP directory entries.

## External Dependencies

Scheduler class operations (`CL_ALLOC`, `CL_ENTERCLASS`, `CL_FORK`, `CL_EXIT`), `/proc`, doors, schedctl, upimutex, contract templates, brands, CPC, lgroup, zones/tasks/projects resource controls, HAT, segkp stack allocation, and DTrace probes.

## Research Notes

This file is a high-risk concurrency core. The most important invariants are balanced LWP accounting, safe publication/reclamation of tid hash tables, correct `p_lwprcnt` transitions around stopped/runnable LWPs, and respecting `/proc` barriers before exposing process state changes.
