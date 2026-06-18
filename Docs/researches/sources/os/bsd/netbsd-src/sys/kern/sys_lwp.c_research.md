# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_lwp.c

## Purpose
Implements user-facing lightweight process syscalls: LWP creation, exit, identity/private data, suspend/continue/wait/kill/detach, park/unpark synchronization, LWP naming, and user control page allocation.

## Main Interfaces
- `sys__lwp_create`, `do_lwp_create`, `mi_startlwp`: create LWPs from user contexts and report traced creation events.
- `sys__lwp_exit`, `sys__lwp_self`, `sys__lwp_getprivate`, `sys__lwp_setprivate`.
- `sys__lwp_suspend`, `sys__lwp_continue`, `sys__lwp_wait`, `sys__lwp_detach`, `sys__lwp_kill`.
- `lwp_park`, `lwp_unpark`, `sys____lwp_park60`, `sys__lwp_unpark`, `sys__lwp_unpark_all`.
- `sys__lwp_setname`, `sys__lwp_getname`, `sys__lwp_ctl`.

## State And Control Flow
LWP creation copies and validates `ucontext_t`, allocates a U-area, calls `lwp_create`, and starts the new LWP only after copying out the new LID. Park/unpark uses `lwp_park_syncobj` and `LW_UNPARKED`/`LW_CANCELLED` flags to avoid lost wakeups between an unpark racing with a later park. Suspend/continue/wait paths hold process locks and use LWP locks around state changes.

## Dependencies And Integration
Depends on process/LWP core lifecycle from `kern_lwp.c`, CPU context validation, UVM U-area allocation, sleep queues, ptrace event reporting, signal delivery, pserialize lookup for unlocked LWP scans, and `lwpctl` shared user/kernel control pages.

## Risks And Edge Cases
- `_lwp_create` must free copied contexts and U-areas correctly on copyout/start failure.
- Self-suspend and all-LWP suspension are checked for deadlock but comments note races around runnable counts.
- `lwp_unpark` handles races where the target has not parked yet by setting `LW_UNPARKED`.
- Timed park returns remaining relative time to userland on relevant paths.
- Detached zombie cleanup may release the process lock through `lwp_free`.

## Filesystem Relevance
Indirect. LWPs are scheduler/thread substrate for filesystem syscalls, blocking I/O, and synchronization, but this file does not implement filesystem behavior.
