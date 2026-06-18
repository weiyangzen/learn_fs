# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_resource.c

This file implements process priority/resource syscalls and per-UID accounting. It covers nice priority, I/O priority, realtime priority, resource usage aggregation, uidinfo hash management, per-user process counts, and socket-buffer accounting.

Priority syscalls:
- `sys_getpriority()` returns the lowest nice value for a process, process group, or user. It uses `pfind()`, `pgfind()`, or `allproc_scan()` and gates visibility through jail checks.
- `sys_setpriority()` applies a nice value to a process, pgrp, or user selection. `donice()` clamps to `PRIO_MIN..PRIO_MAX`, enforces ownership/capability rules, updates `p_nice`, and calls the user scheduler's `resetpriority()` for each LWP.
- `sys_ioprio_get()` and `sys_ioprio_set()` mirror nice-priority selection logic for `p_ionice`.
- `doionice()` clamps to `IOPRIO_MIN..IOPRIO_MAX` and requires scheduling privilege to raise I/O priority.

Realtime priority:
- `sys_lwp_rtprio()` gets/sets `lwp_rtprio` for a specific LWP selected by pid and tid. It validates pid/tid, holds the LWP, restricts changes by ownership and `SYSCAP_NOSCHED`, and disallows unprivileged realtime priority.
- `sys_rtprio()` is the older process-oriented interface and operates on the first LWP in the process.

Resource usage:
- `calcru()` converts a thread's microsecond user/system tick counters into `timeval`s.
- `calcru_proc()` aggregates process-level `p_ru`, live LWP CPU time, and live LWP rusage counters.
- `sys_getrusage()` returns `RUSAGE_SELF` or `RUSAGE_CHILDREN`.
- `ruadd()` accumulates two `struct rusage` values.

UID accounting:
- `uihashinit()` creates the uidinfo hash.
- `uicreate()` allocates, initializes, and inserts a `struct uidinfo`, with race handling if another thread created it first.
- `uifind()` checks current thread credential uidinfo shortcuts before using the hash.
- `uihold()`, `uidrop()`, `uireplace()`, and `uifree()` manage uidinfo references and teardown.
- `chgproccnt()` adjusts per-UID process count and optionally enforces a maximum.
- `chgsbsize()` adjusts per-UID socket buffer usage and scales a caller's high-water mark down when above limit.

Concurrency and permissions:
- Process and pgrp tokens protect selected process mutations.
- The uidinfo hash is protected by `uihash_lock`; individual uidinfo has its own spinlock for embedded state.
- Jail checks prevent cross-prison visibility or modification.

Filesystem/storage relevance:
- Process limits, priorities, UID accounting, and rusage affect filesystem servers, VFS worker behavior, lock-heavy workloads, and per-user resource enforcement.

Notable risk/quirk:
- In the `PRIO_PGRP` branch of `sys_ioprio_get()`, the condition tests `p->p_nice > high` but assigns `p->p_ionice`; this looks inconsistent with the user and process paths and may be a typo.
