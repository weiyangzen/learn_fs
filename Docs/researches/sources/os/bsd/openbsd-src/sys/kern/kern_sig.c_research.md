# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_sig.c

Purpose: Implements signal dispositions, masks, delivery, process/thread stop and continue, traps, coredumps, signal wait/diversion, user return signal posting, and SIGIO ownership.

Signal state:
- `sigprop[]` defines default signal actions: kill, core, stop, continue, ignore, tty stop.
- `signal_init()`, `sigstkinit()`, `sigactsinit()`, and `sigactsfree()` initialize and manage signal action storage.
- `sys_sigaction()` and `setsigvec()` install dispositions, masks, restart behavior, `SA_RESETHAND`, `SA_SIGINFO`, `SA_ONSTACK`, `SA_NOCLDSTOP`, and `SA_NOCLDWAIT`.
- `execsigs()` resets caught signals and signal stack state across exec.
- `sys_sigprocmask()`, `sys_sigpending()`, `dosigsuspend()`, `sys_sigsuspend()`, `sys_sigaltstack()`, and `sigonstack()` handle masks and alternate stacks.

Signal authorization and sending:
- `cansignal()` enforces root, self, shared credentials, same-session SIGCONT, and restricted setugid child signaling rules.
- `sys_kill()`, `sys_thrkill()`, `killpg1()`, `pgsignal()`, and `pgsigio()` deliver to processes, threads, groups, broadcast targets, and SIGIO owners.
- `trapsignal()` records trap signal metadata and delivers immediately when possible.

Delivery engine:
- `ptsignal_locked()` decides target thread, ignored/held/caught/default action, process vs thread pending queues, sleep wakeups, stop handling, SIGCONT handling, and parent notifications.
- `setsigctx()` snapshots action context for `cursig()` and `postsig()`.
- `cursig()` selects pending signals, handles ptrace stops, default stop actions, ignored signals, and deep sleep unwind cases.
- `postsig()` builds `siginfo_t`, invokes MD `sendsig()`, updates masks, or terminates by `sigexit()`.
- `userret()` checks single-thread suspension, pending interval-timer signals, pending normal signals, and restores `sigsuspend` masks.

Thread/process suspension:
- `proc_trap()`, `process_stop()`, `process_continue()`, `proc_stop_setup()`, `proc_stop_finish()`, `process_suspend_signal()`, `proc_suspend_check()`, `single_thread_set()`, and `single_thread_clear()` coordinate ptrace, job-control stops, coredump/single-threading, and thread exit suspension.

Filesystem and coredump relevance:
- `sigexit()` performs coredumps for core-generating signals before `exit1()`.
- `coredump()` enforces `RLIMIT_CORE`, disables copyin checks if configured, handles setugid core policy, opens core files with `BYPASSUNVEIL`, validates regular file/link/mode/owner, truncates it, and calls ELF coredump writing.
- `coredump_write()` writes in `MAXPHYS` chunks, yields between writes, aborts on pending SIGKILL, and logs ENOSPC/write failures.
- `coredump_unmap()` unmaps VM ranges after dumping.

SIGIO:
- `sigio_setown()`, `sigio_getown()`, `sigio_copy()`, `sigio_free()`, and helpers manage async I/O signal ownership for processes or process groups, with session checks and stored credentials.
