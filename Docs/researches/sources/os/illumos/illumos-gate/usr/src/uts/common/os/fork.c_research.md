# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fork.c

## Purpose

`fork.c` implements process creation for user and kernel processes: `forkx`, `forkallx`, branded-zone `vfork`, `newproc()`, process structure allocation, LWP cloning, resource-control accounting, vfork address-space release, and parent waiting.

Read completely: 1,480 lines.

## Main Responsibilities

- Implements syscall entry points `vfork()` and `forksys()`.
- Performs shared fork logic in `cfork()`.
- Allocates and initializes child `proc_t` structures in `getproc()`.
- Duplicates or shares address spaces depending on fork type.
- Clones one LWP for fork1 or all LWPs for forkall.
- Handles process contracts, tasks, pools, projects, zones, sessions, credentials, file tables, and current/root directories.
- Creates kernel processes and init-style user processes through `newproc()`.
- Cleans up partially constructed children on fork failure.
- Releases address spaces in `relvm()`.
- Implements `vfwait()` for parents waiting on vfork children.

## Fork Entry Points

`forksys()` dispatches subcodes:

- `0`: `forkx(flags)` through `cfork(0, 1, flags)`.
- `1`: `forkallx(flags)` through `cfork(0, 0, flags)`.
- `2`: `vforkx(flags)` through `cfork(1, 1, flags)` and marks `t_post_sys`.

The legacy `vfork()` syscall remains for Solaris 10 branded zones.

Allowed flags are `FORK_NOSIGCHLD` and `FORK_WAITPID`.

## `cfork()` Flow

`cfork()` validates flags and policy, rejects `/proc` agent LWPs, holds parent LWPs with `SHOLDFORK1` or `SHOLDFORK`, enters the pool barrier, and calls `getproc()`.

For vfork, the child shares the parent address space, clears watchpoints temporarily, marks `SVFORK`, and uses the parent shared-memory accounting.

For normal fork, it sets `SFORKING`, holds `/proc` state with `sprlock_proc()`, duplicates the address space through `as_dup()`, removes inherited DTrace fasttrap probes from the child, and duplicates shared memory and DTrace helper state.

After address-space setup, it duplicates resource controls, allocates the child LWP directory and tid hash, clones one or all LWPs, attaches the child to process contracts, inherits core settings and process context ops, sets tracing stops, and arranges return values.

## Process Allocation

`getproc()` enforces zone shutdown, task/project/zone process resource controls, global process limits, per-user limits, and privilege checks. It allocates from `process_cache`, initializes locks and process fields, allocates a pid, holds executable vnodes, links the child into pid and active process lists, attaches it to the parent, task, pool, session, orphan list, and child chain, and duplicates user-area state.

It also increments file-table references through `fcntl_add()`/`flist_fork()`, holds cwd/root/cwd refstr, duplicates audit state, copies credentials, process flags, tracing masks, stack/heap layout fields, security flags, and resource-control cached values.

## Kernel Process Creation

`newproc()` creates either class-kernel processes or init-like user processes. Kernel processes are attached to task0/default pool, clear user tracing state, initialize process resource controls, and create a stopped kernel LWP. User init-style creation creates a new task and default rlimit controls before creating the first LWP.

## Cleanup Paths

`fork_fail()` releases file references, pending signals, uid process counts, credentials, file-list storage, cwd/root/executable references, cwd refstr, and brand state.

`forklwp_fail()` removes already-created LWPs from the child process, updates task/project/zone LWP counts, frees door data and LWP templates, removes threads from the global all-thread list, informs the scheduler, fixes lgroup load accounting, and frees thread structures.

Error paths unwind address spaces, shared memory, DTrace helpers, resource controls, task attachment, pid state, pool references, LWP directories, and tid hashes.

## Vfork Release And Wait

`relvm()` handles both vfork and normal exit/exec address-space release. For vfork children it clears `SVFORK`, switches the child to `kas`, notifies the HAT, copies heap/stack and shared-memory accounting back to the parent, restores watched pages, clears parent `SVFWAIT`, and signals the parent.

`vfwait()` waits until the vfork child exits or execs, carefully avoiding stale child references by re-looking up the pid and locking the child before dropping `pidlock`.

## Important Invariants

- Fork failure past each construction phase has a matching unwind path.
- `pool_barrier_exit()` is delayed until the child has enough resource-set identity to be safely visible.
- `pidlock` handoff to `CL_FORKRET()` prevents the child from running and disappearing before scheduler setup completes.
- vfork lock ordering between parent and child is explicitly delicate because the parent may exit once woken.
- `/proc` locks and DTrace probe removal are coordinated before child instrumentation is duplicated.

## Research Relevance

This file matters to filesystem research because fork semantics define file table inheritance, OFD lock preservation context, cwd/root/executable vnode references, address-space duplication for mmap state, and vfork sharing/release behavior. It is also a major consumer of process, task, zone, and resource-control infrastructure.
