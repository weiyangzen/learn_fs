# File Research: sources/os/bsd/freebsd-src/sys/kern/init_main.c

## Purpose
Contains the machine-independent kernel startup path, process 0 construction, init process creation, and the ordered `SYSINIT` execution machinery.

## Key Elements
- Permanent boot objects: `session0`, `pgrp0`, `proc0`, `thread0_st`, `vmspace0`, `initproc`.
- Startup entry point: `mi_startup()`.
- Sysinit structures: `sysinit_list`, `sysinit_done_list`, linker set `sysinit_set`.
- Init process path sysctl: `kern.init_path`.
- Init shutdown timeout sysctl: `kern.init_shutdown_timeout`.
- DDB support: `show sysinit`.

## Startup Ordering
`sysinit_mklist()` turns linker-set entries into a sorted STAILQ using `subsystem` then `order`. `sysinit_add()` merges new sorted sysinit entries into the live list, supporting later additions such as KLD-provided sysinits.

`mi_startup()`:
- Enables verbose boot if `RB_VERBOSE` is set.
- Builds and sorts the sysinit list.
- Iteratively removes the earliest sysinit from `sysinit_list`, appends it to `sysinit_done_list`, and calls it.
- Emits boottrace events at subsystem boundaries.
- Supports optional verbose sysinit printing and DDB symbol lookup.
- Unlocks `Giant` after startup and leaves the original startup thread sleeping forever.

## Process 0 Initialization
`proc0_init()` builds the kernel process and initial thread:
- Initializes process, thread, scheduler, prison, session, process group, pid/tid hash state.
- Creates credentials rooted in uid/gid 0 and prison0.
- Initializes signal actions, fd tables, process descriptors, limits, racct, stats, and vmspace.
- Initializes `vmspace0` and its pmap/map.
- Invokes process/thread init and ctor event handlers.
- Charges root for the kernel process.

`proc0_post()` resets process and thread start/runtime accounting after filesystem time has been established, then updates per-CPU switch timing.

## Init Process
`create_init()` forks process 1 from `thread0` in stopped state, marks it system/in-memory/reaper, gives it separated credentials, and installs `start_init()` as its thread handler.

`kick_init()` later makes init runnable at `SI_SUB_KTHREAD_INIT`.

`start_init()`:
- Mounts root with `vfs_mountroot()`.
- Removes the GELI passphrase environment entry.
- Handles dual-console reporting.
- Reads `init_path` from the kernel environment if present.
- Tries each colon-separated init path.
- Builds exec args with `argv[0] = path` and optional `-s` for single-user mode.
- Calls `kern_execve()` and completes `exec_cleanup()` on `EJUSTRETURN`.
- Panics if no init path can be executed.

## Research Notes
This file is central boot glue rather than one subsystem. It wires together sysinit sequencing, proc0, pid 1, root mounting, and the final transition into userland.
