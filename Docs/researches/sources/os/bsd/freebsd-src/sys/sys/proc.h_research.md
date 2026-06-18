# File Research: sources/os/bsd/freebsd-src/sys/sys/proc.h

Read completely: 1380 lines.

## Purpose
Defines FreeBSD's central process/thread kernel data model and the public/kernel interfaces for process groups, sessions, threads, processes, scheduler-visible state, ptrace/debug flags, process lookup, forking, reaping, suspension, and machine-dependent thread/process hooks.

## Main Elements
- Defines `struct session`, `struct pgrp`, `struct pargs`, `struct rusage_ext`, `struct thread`, `struct thread0_storage`, and `struct proc`.
- Documents extensive locking keys for process, thread, process-group, and session fields.
- Defines thread state machine values, thread flags (`TDF_*`), AST indices (`TDA_*`), debugger flags (`TDB_*`), private thread flags (`TDP_*`, `TDP2_*`), and inhibitor/state macros.
- Defines process state values, process flags (`P_*`, `P2_*`), proctree flags, legacy process status constants, process magic, and switch/reason constants.
- Provides lock macros for process, process spin/stat/itim/prof locks, process group locks, and session locks.
- Provides process hold/release macros (`PHOLD`, `PRELE`) and process copy-on-write generation helpers.
- Exposes PID and process-group hash globals, `allproc`, `proctree_lock`, `proc0`, `thread0`, `vmspace0`, process limits, UMA zones, and process/thread list head types.
- Defines `struct fork_req` and flags for `fork1()` behavior, including process-descriptor and kernel-process creation fields.
- Declares process lookup (`pfind`, `pget`, `tdfind`), process visibility/permission helpers, process-group/session operations, fork/exit/reparent/reap operations, thread allocation/lifecycle/suspension operations, AST scheduling, CPU context hooks, and global stop/resume controls.
- Provides inline helpers for current-thread pflags save/restore, scheduler-private thread storage access, kernel-stack top lookup, and `rusage_ext` reset.
- Declares process and thread eventhandler lists.

## Dependencies And Integration
Integrates nearly every kernel subsystem touching processes: scheduler, signals, credentials, file descriptors, VM spaces, jails, RACCT/RCTL, kqueue, audit, DTrace, ktrace, MAC, procdesc, timers, callouts, turnstiles, sleepqueues, machine-dependent CPU/thread state, and UMA allocation.

## Risk Notes
This is a core ABI/KPI contract. Field ordering, lock annotations, flag meanings, and macro side effects are relied on widely. Changes can break scheduler state, process lifetime rules, ptrace semantics, process reaping, credential checks, or machine-dependent context switching.
