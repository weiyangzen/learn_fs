# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_trap.c

## Purpose
Provides common user-return and asynchronous software trap (AST) handling for trap and syscall paths.

## `userret()`
Runs before returning to user mode:
- Asserts the process is not exiting.
- In diagnostic builds, verifies pending signal AST state for single-threaded processes.
- Charges profiling ticks with `addupc_task()` when process profiling is enabled.
- Calls HWPMC user-return hook when samples are pending.
- Calls `sched_userret()` for scheduler priority/accounting updates.
- Performs strict invariants: no critical section, no locks, no read locks, no shared sx/lockmanager locks, no nofaulting, sleep enabled, not pinned except callchain, no reserved vnode, no deferred stop signals, no wired vslock space.
- With VIMAGE, asserts no leaked current vnet.

## AST Registration
- `struct ast_entry` maps AST slot to flags, thread pflags mask, and handler function.
- Default `TDA_AST` handler is `ast_prep()`, which increments trap count, resets ticks, and updates thread COW generation.
- `ast_register()` installs handlers with memory ordering.
- `ast_deregister()` clears handlers but explicitly does not drain possible in-flight executions.
- `ast_sched_locked()`, `ast_unsched_locked()`, `ast_sched()`, and `ast_sched_mask()` manipulate thread AST bits.

## AST Execution
- `ast_handler()` optionally stores the trapframe in `td_frame`, clears scheduled AST bits, validates user-mode trapframes, then scans registered handlers.
- Handler execution depends on flags:
  - unconditional handlers,
  - handlers requiring a scheduled AST bit,
  - kernel-clear handlers for destructor/cleanup paths,
  - optional thread-pflag constraints.
- `ast()` handles current-thread ASTs and then calls `userret()`.
- `ast_kclear()` clears kernel AST state, including for thread teardown.

## Utility
- `syscallname()` maps syscall code to ABI-specific syscall name, returning `"unknown"` if unavailable.

## Filesystem Relevance
Filesystem syscalls return through this code. The lock and reserved-vnode assertions are important guardrails for VFS/file operation implementations returning to userspace.
