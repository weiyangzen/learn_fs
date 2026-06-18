# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_exit.c

## Role

Implements process and LWP termination, `exit`, extended LWP/process exit, killing peer LWPs, zombie transition, wait/reap semantics, child reparenting, exit callbacks, and asynchronous dead-LWP cleanup. It is closely tied to file descriptor teardown, vmspace release, text vnode/namecache release, kqueue cleanup, jail/reaper behavior, and resource accounting.

## Major Entry Points

- `sys_exit()` terminates the process through `exit1()`.
- `sys_extexit()` can exit only the current LWP when other LWPs remain, or the whole process otherwise.
- `killalllwps()` marks `P_WEXIT`, sets `LWP_MP_WEXIT`, sends `SIGKILL` to all other LWPs, waits until only the current LWP remains, and optionally cleans flags for exec reuse.
- `exit1()` performs full process teardown and never returns.
- `lwp_exit()` performs per-LWP teardown and ends in `cpu_lwp_exit()`.
- `sys_wait4()`, `sys_wait6()`, and `kern_wait()` implement wait semantics, zombie reaping, stopped/continued state reporting, `WNOWAIT`, and wait filtering by pid, pgrp, sid, uid, gid, and jail id.

## Process Exit Flow

- Refuses to let pid 1 die without panicking.
- Cleans varsym state, kills peer LWPs, kills task-leader peers, posts stop/exit tracing events, sets `P_POSTEXIT`, and stores `p_xstat`.
- Runs registered `at_exit` callbacks.
- Stops profiling, clears pending signal sets, terminates real-time timer callout, clears `sigio` ownership, closes and releases the file descriptor table via `fdfree()`, removes peer linkage, and exits SYSV semaphores.
- Releases virtual-kernel state and calls `vmspace_relexit()` early to drop user address-space resources while sleeping is still allowed.
- Handles session-leader controlling terminal shutdown and revoke semantics.
- Performs accounting, destroys ktrace state, releases `p_textvp`, drops `p_textnch`, handles vfork `P_PPWAIT`, and moves the process to the zombie list.
- Releases owned reaper state, reparents children to init or a subreaper, sends parent-death signals, accumulates rusage, posts `NOTE_EXIT`, reparents self to reaper when parent ignores/no-waits `SIGCHLD`, signals parent, frees limits, and exits final LWP.

## LWP Exit and Reaping

- `lwp_exit()` releases user scheduler state, unmaps per-thread shared page, sets `LWP_MP_WEXIT`, exits virtual-kernel LWP state, terminates per-LWP kqueue used by select/poll, drops Linux compatibility callbacks, releases cached credentials and limits, clears per-thread fd cache, waits for `lwp_lock`, folds LWP rusage into process rusage, exits disk/I/O scheduler state, removes non-master LWPs from the RB tree, and queues them to per-CPU dead-LWP taskqueues.
- `lwp_wait()` waits for final thread-exit interlocks (`TDF_MP_EXITSIG`, refs, flags) before stack/thread disposal.
- `lwp_dispose()` releases the process hold, detaches the thread/LWP relationship, frees the LWKT thread, and frees the LWP.
- `deadlwp_init()` creates per-CPU tokens/lists/tasks for dead LWP reaping.

## Wait and Zombie Reaping

- `kern_wait()` validates options, scans children under the parent's token, filters by id type, and handles Linux clone wait behavior.
- For `SZOMB` children and `WEXITED`, it obtains zombie ownership, waits for all LWPs to exit, reaps any remaining LWPs, stalls until references drop, fills status/rusage/siginfo, honors `WNOWAIT`, restores ptrace-attached children to original parents when needed, removes zombie process structures, updates parent child rusage, frees credentials, arguments, signal actions, vmspace, uidpcpu, and `struct proc`.
- Stopped/trapped and continued states are reported without full reaping.
- Parent sleeping is interlocked through `p_waitgen`.

## VFS/File-System Relevance

- `fdfree()` closes process file descriptors during exit.
- `p_textvp` and `p_textnch` are released on exit, matching references acquired by exec/fork.
- `vmspace_relexit()` and `vmspace_exitfree()` release mmap/file-backed VM resources, potentially triggering vnode I/O for unlinked mapped files.
- Controlling terminal cleanup can revoke tty access.
- `kqueue_terminate(&lp->lwp_kqueue)` tears down select/poll event resources held by each LWP.

## Reparenting and Reapers

- `proc_reparent()` safely moves a child between parent child lists by holding old parent, child, and new parent tokens, retrying on races.
- `exit1()` uses `reaper_exit()`, `reaper_get()`, and parent signal settings to decide whether children or the exiting process move to a subreaper.

## Research Notes

- The exit path intentionally releases `p_token` around large vmspace release/free operations to avoid stalling global process scans.
- Zombie reaping is split from exit: exit moves the process to zombie state; wait owns final process structure destruction.
- This file is required context for event notification (`NOTE_EXIT`), text vnode lifetime, descriptor teardown, mmap cleanup, and process-scoped filesystem resource release.
