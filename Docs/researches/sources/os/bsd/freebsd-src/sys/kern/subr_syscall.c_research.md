# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_syscall.c

## Purpose
Provides common syscall entry and return handling used by machine-dependent syscall paths. It centralizes syscall argument fetching, tracing, Capsicum enforcement, audit/DTrace hooks, syscall execution, return value setup, and ptrace syscall-stop behavior.

## Main Flow
- `syscallenter(struct thread *td)`:
  - Increments syscall VM counter and resets per-syscall tick accounting.
  - Updates thread copy-on-write generation if process COW generation changed.
  - Handles traced syscall-entry state and debugger writeback (`TDB_USERWR`).
  - Fetches syscall number/arguments through the process ABI vector.
  - Emits KTRACE and KTR syscall-start events.
  - Stops for `PTRACE_SCE`; if debugger changed user registers/memory, refetches syscall args.
  - Enforces Capsicum capability mode by rejecting non-`SYF_CAPENABLED` syscalls with `ECAPMODE`.
  - Fetches fast signal-block state when required.
  - Handles dynamic syscall thread accounting with `syscall_thread_enter()`/`syscall_thread_exit()`.
  - Fires audit and KDTrace syscall entry/return hooks around `se->sy_call`.
  - Stores the syscall error in `td_errno` unless the syscall used `TDP_NERRNO`.
  - Sets ABI-specific return values via `sv_set_syscall_retval()`.
  - Copies extended error state to userspace when `TDP2_UEXTERR` is active.

- `syscallret(struct thread *td)`:
  - Converts Capsicum violations into `SIGTRAP/TRAP_CAP` when configured.
  - Calls `userret()` to handle scheduler, signal, profiling, and user-return checks.
  - Emits KTRACE syscall-return records.
  - Handles traced syscall-exit stops, including Linux ABI exec-stop compatibility.
  - Clears syscall tracing/debug flags.

## Dependencies
Uses process ABI vectors (`p_sysent`), syscall table entries (`struct sysent`), ptrace flags, Capsicum, audit, KDTrace hooks, KTRACE, and `userret()` from `subr_trap.c`.

## Concurrency and State
- Uses `PROC_LOCK()` around debug/tracing flag updates and ptrace-stop checks.
- Assumes syscall argument and return state is stored in the current thread (`td_sa`, `td_retval`, `td_errno`).
- Dynamic syscall entries may require per-syscall thread enter/exit bookkeeping.

## Filesystem Relevance
All filesystem syscalls pass through this path. This file is where VFS-facing syscalls receive common tracing, capability-mode validation, audit framing, debugger stops, and return-value handling.
