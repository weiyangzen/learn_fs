# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_resource.c

Read completely: 1843 lines.

## Purpose
Implements process priority syscalls, realtime/idle priority conversion, resource limits, rusage accounting, copy-on-write `plimit` management, UID accounting objects, per-user limit counters, and rlimit-usage reporting.

## Main Elements
- Implements `getpriority(2)` and `setpriority(2)` through `kern_getpriority()` and `kern_setpriority()`, supporting process, process-group, and user scopes with Capsicum and visibility/scheduling permission checks.
- `donice()` clamps nice values and requires `PRIV_SCHED_SETPRIORITY` when raising scheduling priority.
- Implements `rtprio(2)` and `rtprio_thread(2)` lookups/updates, translating between `struct rtprio` and scheduler priority classes with `rtp_to_pri()` and `pri_to_rtp()`.
- Supports old 4.3BSD `ogetrlimit()`/`osetrlimit()` compatibility when enabled.
- `kern_proc_setrlimit()` performs privileged hard-limit changes, clamps data/stack/nofile/nproc limits to kernel maxima, updates CPU-limit callouts, updates stack VM protections when soft stack limits change, and uses copy-on-write `struct plimit` replacement.
- `lim_cb()` periodically checks CPU time limits, sends `SIGXCPU` below the hard limit, and kills processes beyond the maximum.
- `getrlimitusage_one()` reports current use for CPU, data, stack, RSS, locked memory, process count, open files, socket buffers, VMEM, ptys, swap, kqueues, umtxs, pipe buffers, and VMM resources.
- Implements `getrusage(2)` via `kern_getrusage()`, with `RUSAGE_SELF`, `RUSAGE_CHILDREN`, and `RUSAGE_THREAD`.
- Maintains precise runtime accounting with `calcru()`, `calccru()`, `calcru1()`, `rufetchtd()`, `rufetch()`, `rufetchcalc()`, `ruxagg()`, and overflow-safe `mul64_by_fraction()`.
- Manages `struct plimit` allocation, hold/free, fork sharing, thread COW synchronization, batch refcount release, and copying.
- Initializes and manages the UID hash table through `uihashinit()`, `uifind()`, `uilookup()`, `uihold()`, and `uifree()`, including per-UID RACCT creation/destruction when `RACCT` is enabled.
- Provides `ui_racct_foreach()` for RACCT/RCTL consumers to iterate UID accounting containers.
- Implements atomic per-user limit counters through `chglimit()` wrappers: process count, socket buffer size, ptys, kqueues, umtxs, pipes, inotify instances/watches, and VMM count.
- Exposes `kern.proc.rlimit_usage` sysctl output for all resources or one selected resource.

## Dependencies And Integration
Integrated with scheduler priority classes, process/session/process-group locking, Capsicum, privilege framework, VM maps and pmaps, file descriptor counting, RACCT, UMTX priority inheritance, callouts, sysctl, and per-UID credential state.

## Risk Notes
This file sits on hot process/resource paths. Risk centers on lock ordering between proc locks, stat locks, thread locks, UID hash locks, and VM references; accurate monotonic runtime conversion across long uptimes; copy-on-write limit lifetimes; and per-user counters staying balanced on all allocation/free paths.
