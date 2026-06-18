# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_fork.c

## Purpose
Implements process fork, vfork, thread fork, kernel/system process creation support, pid/tid allocation, and machine-independent trampoline setup for new threads.

## Main Responsibilities
- Implements `sys_fork()`, `sys_vfork()`, and `sys___tfork()`.
- Allocates thread (`struct proc`) state in `thread_new()`.
- Initializes process (`struct process`) state in `process_initialize()` and `process_new()`.
- Enforces global and per-user thread/process limits in `fork_check_maxthread()` and `fork1()`.
- Schedules new runnable threads with `fork_thread_start()`.
- Creates user threads with `thread_fork()`.
- Allocates random tids and pids with `alloctid()` and `allocpid()`.
- Prevents fast pid reuse via `oldpids[]` and `freepid()`.
- Performs trampoline setup in `proc_trampoline_mi()`.

## Key Fork Flow
`fork1()` checks limits, increments process counts, allocates a U-area, creates a proc and process, copies/shares fd table and vmspace according to flags, copies signal/credential/resource state, performs `cpu_fork()`, assigns pid/tid, links into global pid/process lists and parent/pgid lists, handles ptrace fork reporting, clears embryo state, schedules the child, sends fork knotes, updates fork stats, and handles `FORK_PPWAIT` synchronization.

## Thread Fork Flow
`thread_fork()` creates a new `P_THREAD` proc in the existing process, shares fd/vmspace pointers, copies CPU context with stack/TCB, links into `ps_threads`, copies suspend/single-thread state if needed, optionally copies out tid, and schedules it.

## Key Flags
- `FORK_FORK`, `FORK_VFORK`, `FORK_PPWAIT`
- `FORK_SHAREVM`, `FORK_SHAREFILES`
- `FORK_PTRACE`
- `FORK_NOZOMBIE`, `FORK_SYSTEM`, `FORK_IDLE`

## Dependencies
Uses UVM fork/share, fd copy/share, signal action copy, limits, credentials, scheduler, process groups, ptrace, ktrace, kqueue process fork notes, and machine-specific `cpu_fork()`.

## Research Notes
PIDs are randomized except PID 1. TIDs are randomized within `TID_MASK` and exposed to userland with `THREAD_PID_OFFSET`.
