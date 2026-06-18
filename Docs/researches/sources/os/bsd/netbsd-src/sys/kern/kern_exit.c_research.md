# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_exit.c

Read completely: 1340 lines.

Implements NetBSD process termination, zombie collection, wait-family system calls, and process reparenting support. This is the main exit/wait side of the process lifecycle, paired with `kern_fork.c` and integrated with signals, ptrace/procfs, kqueue process notes, accounting, VFS/file descriptor teardown, and scheduler cleanup.

Core exit flow:
- `sys_exit()` prevents repeated process-wide exit by checking `PS_WEXIT`, then calls `exit1()` with `p->p_lock` held.
- `exit1()` marks the process exiting, forces all other LWPs out with `exit_lwps()`, handles stop-on-exit tracing, drains pending signals, marks the process dying, and runs `lwp_thread_cleanup()` so global LWP lookup can no longer find it.
- Resource teardown releases lwpctl, proc references, POSIX timers, RAS state, file descriptors, cwd state, exit hooks, signal actions, process accounting, ktrace descriptors, emulation exit hooks, VM space, profiling, fstrans state, LWP/proc specificdata, and PCU state.
- Session leader cleanup detaches and potentially revokes the controlling terminal, sends `SIGHUP` to the foreground process group, and clears session leader state.
- Children are reparented to `initproc`; traced children are detached/reparented and killed as orphaned traced processes.
- The exiting process is moved from `allproc` to `zombproc`, marked `SDEAD` and later `SZOMB`, has its final LWP converted to `LSZOMB`, notifies kqueue via `knote_proc_exit()`, signals or wakes the parent, drops `p_reflock`, and finally switches away permanently.

Wait and collection:
- `do_sys_waitid()` and `do_sys_wait()` implement common wait logic for `wait4`/`wait6`-style interfaces, filling status, `wrusage`, and optional `siginfo_t`.
- `sys___wait450()` and `sys_wait6()` handle user copyout for legacy and modern wait entry points.
- `match_process()` checks child selection criteria by `P_ALL`, `P_PID`, `P_PGID`, `P_SID`, `P_UID`, and `P_GID`, fills approximate or final `siginfo_t`, and snapshots resource usage for stopped or exited children.
- `find_stopped_child()` scans a parent's children for zombies, stopped/traced children, and continued children, validates wait options, handles `WAIT_MYPGRP`, sleeps on `p_waitcv` when needed, and accounts for ptrace-reparented children via `debugged_child_exists()`.
- `proc_free()` performs final zombie collection: handles traced children that must be returned to an original parent, rolls child resource usage into the parent, frees PID and LWP resources, leaves the process group, releases credentials/limits/stats/text vnode/path/locks/CVs, and frees the proc structure.

Reparenting and tracing:
- `exit_psignal()` builds exit signal information, using `CLD_EXITED`, `CLD_KILLED`, or `CLD_DUMPED` for `SIGCHLD`, and includes pid, uid, and CPU time snapshots.
- `proc_changeparent()` marks a process traced, remembers its original parent, sets `PSL_CHTRACED` on the old parent, and reparents under `proc_lock`.
- `proc_reparent()` moves a child between parent child lists, adjusts stopped-child counters for zombies/dead/unwaited stopped processes, and normalizes `SIGCHLD` when reparenting to init.

Concurrency and invariants:
- `exit1()` starts with only `p->p_lock` held and uses explicit transitions through `proc_lock`, `p_reflock`, LWP locks, tty lock, and scheduler locks.
- The code carefully wakes vfork parents waiting on `PL_PPWAIT` after VM teardown to avoid deadlock.
- Once the process reaches the no-sleep section after parent notification, only machine-dependent LWP cleanup and final `mi_switch()` remain.
- `proc_free()` assumes the zombie is unreachable after list removal and intentionally stops doing normal locking after the final resource-release boundary.

Risks and notes:
- `initproc` death is fatal and panics immediately.
- `find_stopped_child()` has special handling for `SDEAD` children to avoid returning to userland during the short dying-to-zombie transition.
- Several wait idtypes are placeholders (`P_CID`, `P_PSETID`, `P_CPUID`).
- Traced-child reparenting is subtle: wait may need to block even when a matching child has been temporarily stolen by a debugger.
