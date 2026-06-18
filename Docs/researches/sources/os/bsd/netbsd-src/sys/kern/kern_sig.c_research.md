# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_sig.c

Read completely: 2688 lines.

Implements NetBSD's kernel signal subsystem: signal action storage, pending signal queues, signal delivery, debugger/ptrace signal stops, process stop/continue state, signal-context save/restore, process-group signaling, core-dump termination, and kqueue signal filters.

Core state and initialization:
- `signal_init()` creates pool caches for `struct sigacts` and `ksiginfo_t`, initializes the process-stop callout, and registers a kauth listener for signal authorization.
- `siginit()` builds global masks for continue, stop, vfork-stop, and unmaskable signals, initializes process-0 signal state, ignored defaults, per-LWP pending queues, and default action flags.
- `sigactsinit()`, `sigactsunshare()`, and `sigactsfree()` manage shared or copied per-process signal actions with reference counts and a private mutex.

Pending signal queues:
- `ksiginfo_alloc()`/`ksiginfo_free()` manage `ksiginfo_t` lifetime, avoiding allocation for empty signal-info records where possible.
- `sigput()` adds pending signal information to either process or LWP queues, coalescing non-realtime signals and enforcing `SIGQUEUE_MAX`.
- `sigget()` and `siggetinfo()` select pending signals, remove one queued info record, manufacture `SI_NOINFO` when needed, and keep the signal bit set if multiple queued records remain.
- `sigclear()` and `sigclearall()` remove pending signals and move queued info records to a drain list for later freeing.

Signal posting and delivery:
- `kpsignal2()` is the central process-signal routine. It handles ignored signals, traced processes, process-vs-LWP delivery, stop/continue signal cancellation, signal waiters, pending queue insertion, and wakeup/notification of runnable or sleeping LWPs.
- `sigpost()` marks an LWP with `LW_PENDSIG`, wakes interruptible sleeps, restarts stopped LWPs for `SIGCONT`, promotes priority for default-kill signals, and decides whether an LWP can take the signal immediately.
- `issignal()` is the user/kernel-boundary selector for the current LWP. It processes ptrace stops, ignored/default actions, stop signals, pending per-LWP before per-process signals, and returns the signal to catch or terminate with.
- `postsig()` commits to a selected signal, updates masks for `sigsuspend`/normal delivery, extracts signal info, emits ktrace/DTrace probes, calls `sigexit()` for default-kill actions, or invokes the emulation signal sender.
- `sendsig()` dispatches between sigcode, legacy sigcontext, and siginfo trampoline versions; `sendsig_reset()` applies handler reset and mask changes after delivery.

Process stop, continue, and tracing:
- `proc_stop()`, `proc_stop_lwps()`, `proc_stop_done()`, and `proc_stop_callout()` coordinate stopping all LWPs, including races where an LWP enters interruptible sleep after `PS_STOPPING`.
- `sigswitch()` and `sigswitch_unlock_and_switch_away()` move the current LWP into stopped state and perform the scheduler switch.
- `proc_unstop()` resumes a stopped process, moving stopped LWPs back to sleep or run queues as appropriate.
- `trapsignal()`, `eventswitch()`, `eventswitchchild()`, and `proc_stoptrace()` integrate traps, ptrace events, syscall-entry/syscall-exit tracing, and synthetic `SIGTRAP` info with process stops.
- `sigchecktrace()` handles debugger-supplied signals while respecting pending `SIGKILL`.

Exit and core dump:
- `sigexit()` handles fatal-signal termination, coordinates multi-LWP core dumps, suspends peer LWPs while registers are dumpable, calls coredump module hooks, logs optional core status, applies PaX segvguard, clears `PS_WCORE`, and enters `exit1()`.
- `coredump_netbsd()`, `coredump_netbsd32()`, `coredump_elf32()`, and `coredump_elf64()` are module-hook wrappers.

Other interfaces:
- `killpg1()`, `pgsignal()`, `kpgsignal()`, `psignal()`, and `kpsignal()` implement process-group, broadcast, and process-specific sends with kauth checks and optional fd lookup by file data pointer.
- `getucontext()` and `setucontext()` copy signal mask, stack, link, and machine context while coordinating with `p_lock`.
- `sigismasked()` checks ignored or LWP-masked state.
- `filt_sigattach()`, `filt_sigdetach()`, and `filt_signal()` implement EVFILT_SIGNAL through the process klist.

Concurrency and notes:
- Most process signal mutation requires both `proc_lock` and `p_lock`; per-action mutation uses `sa_mutex`.
- Memory barriers protect pending-signal visibility before `LW_PENDSIG` is set.
- Several comments note allocations/freeing while locks are held and legacy SMP concerns.
- The stop path is deliberately conservative because parent notification must wait until all LWPs have stopped at least once.
