# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pid.c

## Purpose

`pid.c` implements PID allocation, PID hash lookup, `/proc` slot management, persistent process locks, process lookup with zone visibility, `/proc` synchronization locks, driver process references, process signaling, and per-UID per-zone process counts.

Read completely: 826 lines.

## Main Responsibilities

- Initializes global PID and `/proc` directory state.
- Allocates and frees `struct pid` objects and `/proc` slots.
- Maintains `pidlock`, `pidlinklock`, `pr_pidlock`, per-process persistent locks, and per-slot condition variables.
- Finds processes and process groups subject to zone restrictions.
- Coordinates `/proc` users with process lifetime through `P_PR_LOCK`.
- Provides DDI process references for drivers.
- Maintains process counts by UID and zone.

## PID and `/proc` State

`pid0` is the static PID object for sched/proc0. `pidhash` stores active PID objects, with `pid_hashsz` sized from `v.v_proc / pid_hashlen`.

`procdir` is an array of `union procent` entries used as `/proc` slots. Free entries link through `procentfree`; allocated entries point at `proc_t`.

`proc_lock` is a persistent array of process locks. `pid_getlockslot()` maps proc slots to lock slots with a stride intended to reduce cache-line false sharing while preserving one-to-one slot mapping.

## Allocation and Exit

`pid_init()` allocates hash buckets, `procdir`, per-slot CVs, and persistent process locks; initializes sched as process 0; builds the free `/proc` slot list; inserts `pid0`; and initializes UID process count hashing.

`pid_setmin()` sets PID allocation lower bounds, honoring `jump_pid`.

`pid_allocate()` allocates a `struct pid`, optionally reserves a `/proc` slot, either installs an explicit early PID or loops through `mpid` to find a free PID, hashes the PID object, and wires `p_pidp` and `p_lockp` into the process when `PID_ALLOC_PROC` is requested.

`proc_entry_free()` marks a PID inactive for `/proc` and returns the slot to `procentfree`.

`pid_exit()` removes a process from its process group, releases its session, frees its `/proc` slot, removes it from the active process list, releases the PID, destroys credential lock state, frees the process cache object, decrements global process count, and decrements task/project/zone process counts.

`pid_rele()` unlinks a non-`pid0` PID from the hash table and frees it.

## Lookup and Zone Semantics

`prfind_zone()` finds a live process by PID under `pidlock`, returning it only if the target zone is visible or `ALL_ZONES` is requested.

`prfind()` applies global-zone versus current-zone visibility automatically.

`pgfind_zone()` and `pgfind()` do the same for process-group heads via `pid_pglink`.

`pid_entry()` returns a process for a `/proc` slot when the slot is active and the process is not still `SIDL`.

## `/proc` Synchronization

`sprtrylock_proc()` sets `P_PR_LOCK` on a fully created, non-system, non-exiting process. It returns invalid-state, already-locked, or success status.

`sprlock_zone()` repeatedly looks up a process, takes its `p_lock`, and sets `P_PR_LOCK`, waiting on the per-slot CV if another `/proc` user owns it. In panic context, it returns with just `p_lock`.

`sprwaitlock_proc()` waits for `P_PR_LOCK` to clear and returns with the lock dropped because the process pointer may no longer be valid.

`sprlock_proc()` applies the same lock protocol to an already locked process.

`sprunlock()` clears `P_PR_LOCK`, signals waiters, and drops `p_lock`. If the process received SIGKILL while locked, it restarts stopped LWPs with `TS_XSTART | TS_PSTART` so SIGKILL can be observed.

## Signaling and Driver References

`signal()` sends a signal to every process in a process group.

`prsignal()` sends to the process referenced by a `struct pid` if the `/proc` slot is still active.

`proc_ref()` holds the current process PID for driver use. `proc_unref()` releases it. `proc_signal()` sends a signal through a held PID reference and reports whether the process has gone inactive.

## UID/Zone Process Counts

`upcount_init()` sizes a hash table based on physical memory.

`upcount_inc()` increments the process count for a `(uid, zoneid)` pair, allocating a new entry if necessary. It may drop and reacquire `pidlock` for sleeping allocation, then restarts the lookup.

`upcount_dec()` decrements and frees zero-count entries, panicking if the pair is missing.

`upcount_get()` returns the current count or zero.

## Notable Invariants

- `pidlock` is the global process lock for process list and process lookup callers.
- `pidlinklock` protects PID hash and `/proc` free-slot state.
- PID objects can outlive processes via references, but `pid_prinactive` marks the `/proc` slot inactive.
- Persistent locks avoid dereferencing freed process memory after waits.
- Zone-aware lookup prevents non-global zones from seeing other zones' processes.

## Research Relevance

This file is important for any filesystem code that walks processes, signals owners, uses `/proc`, dumps process state, or coordinates with zones. It also shows panic-sensitive locking behavior used by `dumpsys()`-adjacent walkers.
