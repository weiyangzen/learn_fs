# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_fork.c

Read status: complete file reviewed.

This file implements process creation and rfork variants, including `fork`, `vfork`, `rfork`, process descriptors, PID allocation, non-process rfork unsharing, child process initialization, vfork parent waiting, and child return-to-userland setup.

Main entry points include `sys_fork`, `sys_pdfork`, `sys_vfork`, `sys_rfork`, `sys_pdrfork`, `fork1`, `fork_exit`, and `fork_return`. Internal helpers include `sysctl_kern_randompid`, `fork_findpid`, `fork_norfproc`, `do_fork`, `ast_vfork`, and `fork_init`.

Syscall wrappers populate `struct fork_req` with appropriate flags. `fork` uses `RFFDG | RFPROC`; `pdfork` adds `RFPROCDESC`; `vfork` uses `RFPPWAIT | RFMEM`; `rfork` accepts user flags with validation and maps `RFSPAWN` to a vfork-like spawn mode that drops caught signals; `pdrfork` combines rfork semantics with process descriptor creation.

PID allocation is handled by `fork_findpid`, using `lastpid`, optional `kern.randompid`, `pid_max`, and proc id bitmaps for pid, process group, session, and reaper ids. It avoids PID collisions with other id namespaces and supports `RFHIGHPID` for boot-time high pid allocation.

`fork1` validates flags, enforces process descriptor constraints, handles rfork-without-`RFPROC` by calling `fork_norfproc`, increments global `nprocs` against `maxproc`, serializes with process-group signal delivery via `pg_killsx`, optionally single-threads the parent, allocates a procdesc fd, allocates/recycles `proc` and first `thread`, forks or shares vmspace, performs swap reservation, copies credentials, initializes RACCT/MAC state, enforces `RLIMIT_NPROC`, allocates a process knlist, and calls `do_fork`. Failure paths unwind vmspace, proc refs, procdesc fd, credentials, RACCT, MAC, and process counts.

`fork_norfproc` supports rfork operations that alter the current process rather than create a new one. It may single-thread the process, calls `vm_forkproc` with no child proc, clears or unshares file descriptor/path tables for `RFCFDG`/`RFFDG`, then releases the single-thread boundary.

`do_fork` performs the actual child initialization. It copies selected proc/thread fields, assigns PID, links into allproc, prison, pid hash, and tid hash, allocates/copies fd and path descriptors according to RFCFDG/RFFDG/share flags, sets scheduler state, copies signal actions or shares them, applies spawn/kernel-process signal handling flags, copies text vnode/binname refs, inherits selected flags, forks limits/COW/thread state/stats, handles RFTHREAD peer lists, inserts the child into process group and parent/reaper lists, calls `vm_forkproc`, updates fork/vfork/rfork/kthread counters, initializes procdesc state, invokes process_fork handlers, marks `PRS_NORMAL`, notifies DTrace, arranges vfork parent wait state, emits `knote_fork`, handles ptrace fork events, completes RACCT fork accounting, and either makes the child runnable or returns it stopped.

`ast_vfork` enforces vfork parent synchronization by waiting while the child has `P_PPWAIT`, handling suspension checks, then optionally reporting `PTRACE_VFORK`. `fork_init` registers this AST. `fork_exit` is the machine-independent entry for new child threads from MD trampoline code: it finishes scheduler fork state, stashes dead threads, calls the supplied child callout, handles erroneous kernel-thread returns, invokes ABI schedtail, and enters `userret`. `fork_return` handles ptrace stop-at-fork and syscall-exit reporting, kills the child if its prison died mid-fork, and emits KTRACE syscall return records.

Integration points include process accounting, jails, MAC, RACCT, Capsicum process descriptors, ptrace, kqueue `NOTE_FORK`, DTrace, VM/swap, fd/path descriptors, pgrp signal serialization, proc id bitmaps, scheduler hooks, and syscall return conventions.

Risk areas are failure unwinding after partial child visibility, process count and uid count accounting, `pg_killsx` signal serialization, vfork `P_PPWAIT` wakeups, procdesc initialization ordering, PID namespace collision checks, ptrace fork reparenting, RFTHREAD peer cleanup, and preserving parent/child locks in the expected order.
