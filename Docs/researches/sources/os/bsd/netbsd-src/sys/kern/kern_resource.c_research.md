# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_resource.c

## Purpose

`kern_resource.c` implements process resource controls and accounting: priority/nice syscalls, resource limits, resource usage accounting, process limit copy-on-write, core-name sysctls, and per-process rlimit/stop-flag sysctl nodes.

## Main Responsibilities

- Registers a kauth listener for:
  - nice/priority changes;
  - resource limit get/set authorization.
- Implements:
  - `getpriority`
  - `setpriority`
  - `setrlimit`
  - `getrlimit`
  - `getrusage`
- Maintains max data/stack limits:
  - `maxdmap`
  - `maxsmap`
- Computes runtime/resource usage:
  - `addrulwp()`
  - `calcru()`
  - `getrusage1()`
  - `ruspace()`
  - `ruadd()`
  - `rulwps()`
- Manages `struct plimit` lifetime and copy-on-write:
  - `lim_copy()`
  - `lim_addref()`
  - `lim_privatise()`
  - `lim_setcorename()`
  - `lim_free()`
- Manages pstats copy/free:
  - `pstatscopy()`
  - `pstatsfree()`
- Implements `CTL_PROC` sysctl helpers for:
  - PaX flags;
  - core-name get/set;
  - stop-on-fork/exec/exit flags;
  - rlimit soft/hard values.

## Priority Handling

- `sys_getpriority()` supports `PRIO_PROCESS`, `PRIO_PGRP`, and `PRIO_USER`.
- `sys_setpriority()` applies `donice()` to the selected process/process group/user set.
- `donice()`:
  - requires target process lock;
  - checks owner/root-style permission;
  - clamps nice value to `PRIO_MIN..PRIO_MAX`;
  - asks kauth for `KAUTH_PROCESS_NICE`;
  - calls `sched_nice()`.

## Resource Limits

- `sys_setrlimit()` copies in a user `struct rlimit` and delegates to `dosetrlimit()`.
- `dosetrlimit()`:
  - validates limit index and `cur <= max`;
  - avoids work when unchanged;
  - asks kauth for `KAUTH_PROCESS_RLIMIT` set permission;
  - privatizes the process limit structure;
  - clamps data, stack, file, process, and LWP limits to kernel maxima;
  - for stack limit changes, rejects limits below current stack usage and adjusts VM map protections for newly accessible/inaccessible stack pages;
  - stores the limit under `pl_lock`.
- `sys_getrlimit()` copies the selected rlimit out under `p_lock`.

## Runtime and Usage Accounting

- `addrulwp()` adds an LWP’s accumulated runtime and, if currently running, estimates the active time slice since `l_stime`.
- `calcru()`:
  - combines process and LWP runtime;
  - apportions elapsed runtime among user/system/interrupt ticks;
  - keeps reported user/system times monotonic.
- `getrusage1()` handles `RUSAGE_SELF` and `RUSAGE_CHILDREN`.
- `ruspace()` fills memory-size fields from `vmspace`.
- `rulwps()` folds per-LWP usage into process usage.

## `plimit` Copy-On-Write

- Limits are shared after fork until mutation.
- `lim_copy()` deep-copies rlimits and core-name data, carefully handling races where core-name length changes while copying.
- `lim_privatise()` installs a writeable private copy and chains the old shared limit through `pl_sv_limit` so readers using unlocked pointers are not invalidated too early.
- `lim_free()` uses reference-count release/acquire barriers, frees non-default core-name storage, destroys the lock, and follows `pl_sv_limit` chains.

## Sysctl Support

- `sysctl_proc_findproc()` resolves a PID or current process and takes `p_reflock` where possible.
- `sysctl_proc_paxflags()` exposes read-only PaX flags.
- `sysctl_proc_corename()`:
  - gets/sets process core file name;
  - requires process visibility and `KAUTH_PROCESS_CORENAME`;
  - validates names must be `core`, `/core`, or end in `.core`.
- `sysctl_proc_stop()` gets/sets stop flags for fork, exec, and exit.
- `sysctl_proc_plimit()` gets/sets individual soft/hard rlimit values through `dosetrlimit()`.
- `sysctl_proc_setup()` builds the `CTL_PROC.PROC_CURPROC` tree.
