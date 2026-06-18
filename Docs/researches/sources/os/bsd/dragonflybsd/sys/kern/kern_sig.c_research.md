# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_sig.c

## Purpose

`kern_sig.c` implements DragonFlyBSD signal state, permission checks, process/LWP signal delivery, stop/continue handling, signal waits, signal posting to user mode, core dump policy, `kill` family syscalls, `SIGIO` delivery, and kqueue signal filters.

## Signal State And User APIs

- Signal metadata:
  - `sigproptbl` maps each signal to default properties such as kill, core, stop, ignore, continue, unmaskable, and checkpoint.
  - `sigprop()` and `sig_ffs()` are local helpers for property lookup and first-pending-signal lookup.
  - `sigsetfrompid()` records sender pid/uid in `ps_frominfo`.
- Action/mask setup:
  - `kern_sigaction()` and `sys_sigaction()` read/update handlers, catch masks, restart behavior, altstack flags, reset/nodefer/info flags, and `SIGCHLD` `SA_NOCLD*` state.
  - `siginit()` initializes ignored-by-default signals and global cantmask state.
  - `execsigs()` resets caught signals and altstack state on exec.
  - `kern_sigprocmask()` and `sys_sigprocmask()` update the current LWP mask and interlock with signal-reference waits.
  - `kern_sigpending()`, `sys_sigpending()`, `kern_sigsuspend()`, `sys_sigsuspend()`, `kern_sigaltstack()`, and `sys_sigaltstack()` provide pending, suspend, and alternate-stack behavior.

## Delivery And Stop Logic

- Send entry points:
  - `kern_kill()` supports process, LWP-specific, process-group, and broadcast signaling with capability checks for PID 1.
  - `sys_kill()` and `sys_lwp_kill()` wrap `kern_kill()`.
  - `dokillpg()`, `killpg_all_callback()`, `gsignal()`, and `pgsignal()` implement group/broadcast signaling with process-group lock interlocks against fork.
  - `trapsignal()` posts trap-originated signals to the specific faulting LWP and can directly invoke the user send-signal ABI when immediately catchable.
- Core delivery:
  - `ksignal()` delegates to `lwpsignal()`.
  - `lwpsignal()` handles ignored signals, traced processes, stop/continue side effects, stopped-process behavior, generic signal placement, LWP-specific placement, default stop action, `SIGKILL` wakeup, and kqueue notification.
  - `find_lwp_for_signal()` chooses an eligible LWP, preferring a preempted/current runnable LWP, then interruptible sleepers, then stopped LWPs.
  - `lwp_signotify()` and `lwp_signotify_remote()` wake or interrupt target LWPs locally or through IPIs.
- Stop/continue:
  - `proc_stop()` marks a process `SSTOP` or `SCORE`, updates stopped-thread counts, signals/wakes the parent when all LWPs stop, and notifies runnable threads.
  - `proc_unstop()` clears a matching stopped state and wakes/schedules stopped or sleeping LWPs.
  - `proc_stopwait()` waits for all other LWPs to enter stopped state during core dumping.

## Signal Consumption

- `kern_sigtimedwait()`, `sys_sigtimedwait()`, and `sys_sigwaitinfo()` temporarily adjust masks to consume selected pending signals with optional timeout and return `siginfo_t`.
- `iscaught()` reports whether a pending signal should interrupt/restart a syscall.
- `issignal()` is the main pending-signal evaluator used near syscall/trap return. It handles masks, traced stops, ignored signals, checkpoint signals, default stop behavior, default termination, and caught signals.
- `postsig()` removes the pending signal, handles handler reset, updates the current mask/return mask, accounts delivery, and invokes the process ABI `sv_sendsig()`.
- `sigexit()` forces signal termination, stops peer LWPs for core dumps, invokes `coredump()`, logs abnormal exits, and exits via `exit1()`.

## Core Dumps And Miscellaneous Signal Hooks

- `expand_name()` expands `kern.corefile` `%N`, `%P`, and `%U` substitutions into a bounded path.
- `coredump()` checks SUGID/core sysctls and RLIMIT_CORE, creates and exclusively locks the output vnode, verifies regular-file/single-link/owner constraints, truncates it, and delegates to `sv_coredump()`.
- `sys_nosys()` sends `SIGSYS` and returns `EINVAL`.
- `pgsigio()` sends `SIGIO`/`SIGURG` using stored credentials to a process or process group.
- `filt_sigattach()`, `filt_sigdetach()`, and `filt_signal()` implement signal kqueue filtering.

## State And Dependencies

The file manipulates `proc`, `lwp`, `sigacts`, process groups, kqueue lists, process/LWP tokens, LWP spinlocks, and pending signal sets. It depends on scheduler wakeup semantics from `kern_synch.c`, process lifecycle/exit code, VFS/namecache for core files, capability checks, tracing hooks, virtual-kernel trap redirection, and ABI-specific `sv_sendsig`/`sv_coredump`.

## Risks And Invariants

Correctness depends on token ordering and carefully distinguishing process-pending from LWP-pending signals. Generic delivery uses `p_sigirefs` to avoid races with `sigsuspend`/`pselect`-style mask windows. Stop and core-dump paths must count LWPs exactly once. Signal waits note an existing limitation where reposting after copyout failure can transform a thread-specific signal into a process signal.
