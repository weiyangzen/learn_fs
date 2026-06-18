# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_racct.c

## Purpose
Implements FreeBSD RACCT resource accounting and its integration with optional RCTL resource controls. It tracks per-process and container resource usage for users, login classes, and jails, enforces denyable allocations when RCTL is enabled, and periodically updates decaying resources such as CPU and I/O rates.

## Major Responsibilities
- Defines RACCT resource type flags in `racct_types[]`: reclaimable, inheritable, denyable, decaying, sloppy, and million-scaled resources.
- Allocates and destroys `struct racct` instances with `racct_create()` and `racct_destroy()`.
- Adds, sets, subtracts, and force-updates process and credential resource usage.
- Propagates usage to real UID, jail hierarchy, and login-class RACCT containers.
- Integrates fork/exit lifecycle through `racct_proc_fork()`, `racct_proc_fork_done()`, and `racct_proc_exit()`.
- Moves accounting between credentials on credential changes through `racct_proc_ucred_changed()`.
- Tracks CPU runtime, wallclock, percent CPU, and decaying I/O resources.
- Implements process throttling through AST scheduling and a `racctd` kernel process.

## Accounting Flow
- `racct_add_locked()` optionally calls `rctl_enforce()` before increasing denyable resources.
- `racct_set_locked()` computes a diff from the current process amount and propagates positive or negative deltas to credential containers.
- `racct_sub()` requires droppable resources and asserts that released amount does not exceed process usage.
- `racct_add_cred_locked()` and `racct_sub_cred_locked()` update real UID, all containing prisons, and login class.
- `racct_sub_racct()` clamps sloppy/decaying drops to zero and asserts exact accounting for normal reclaimable resources.

## Periodic Worker
- `racctd()` runs once per second.
- It decays container I/O throttles, walks all processes under `allproc_lock`, updates CPU/wallclock usage, updates percent CPU, then performs a second pass to throttle or wake processes based on PCPU availability.
- It updates UID, login-class, and jail container PCPU after process accounting is refreshed.

## Locking and Lifetime Model
- `racct_lock` serializes RACCT state.
- Process resource operations require `PROC_LOCK(p)` when dereferencing `p_ucred`.
- Container iteration uses callbacks that acquire and release `racct_lock`.
- Process exit zeroes PCPU, drops reclaimable resources, releases RCTL state, and destroys the process RACCT under lock.

## Key Interfaces
- Allocation/lifetime: `racct_create()`, `racct_destroy()`.
- Process usage: `racct_add()`, `racct_add_force()`, `racct_set()`, `racct_set_force()`, `racct_set_unlocked()`, `racct_sub()`.
- Credential/container usage: `racct_add_cred()`, `racct_sub_cred()`, `racct_move()`.
- Limits: `racct_get_limit()`, `racct_get_available()`.
- Lifecycle: `racct_proc_fork()`, `racct_proc_fork_done()`, `racct_proc_exit()`, `racct_proc_ucred_changed()`.

## Notable Edge Cases
- RACCT can be compiled/tuned disabled; almost every public entry returns early when `racct_enable` is false.
- `racct_proc_fork()` rolls back with `racct_proc_exit(child)` if inheritable accounting or NPROC/NTHR charging fails.
- Kernel/system processes and low-CPU processes are exempt from throttling.
- Disk I/O accounting uses current process charging and is force-added because these limits are not denyable.
