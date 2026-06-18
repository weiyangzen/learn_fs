# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sig.c

Implements core illumos signal delivery, signal selection, process/thread stops, default actions, signal queues, `SIGCLD` notification, real-time profiling signal dispatch, and 32-bit `siginfo` conversion.

Key global policy:
- Defines canonical masks: `nullsmask`, `fillset`, `cantmask`, `cantreset`, `ignoredefault`, `stopdefault`, `coredefault`, and `holdvfork`.
- Integrates with `/proc`, DTrace, audit, process contracts, `signalfd`, scheduler control signal blocking, and process/thread lifecycle flags.
- Tracks user-thread stop requests with `num_utstop`, `utstop_cv`, and `thread_stop_lock`.

Signal posting:
- `psignal()` posts to a process; `tsignal()` posts to a thread.
- `sigtoproc()` handles directed and process-wide posting, including SIGKILL, SIGCONT, job-control stop signals, ignored-signal discard, `sigfd` poll wakeups, and external-contract signal tracking.
- `eat_signal()` marks a thread for signal checking and wakes or pokes it when possible.
- `sig_discardable()` avoids unnecessary queueing when a signal is ignored, unblocked, untraced, not waited for, and the process is single-threaded.

Signal selection and stopping:
- `issig()` dispatches to `issig_justlooking()` or `issig_forreal()`.
- `issig_justlooking()` is a lockless fast check for pending work before doing the expensive path.
- `issig_forreal()` handles DTrace-generated stops/signals, process kill/exit state, single-step suppression, `/proc` stop requests, checkpoint/hold/pause stops, current signals, pending thread/process signals, tracing stops, and `SIGCLD` reposting.
- `fsig()` selects the next unheld signal, prioritizing `SIGKILL` and `SIGPROF`, respecting vfork and `lwp_nostop`.
- `isjobstop()`, `jobstopped()`, and `stop()` implement job-control and `/proc` stop semantics, including parent notifications and thread-state transitions.

Signal action execution:
- `psig()` performs the current signal action.
- For handlers, it prepares optional `siginfo`, updates masks, honors reset/no-defer/restart/on-stack flags, calls `sendsig()` or `sendsig32()`, and converts failed handler setup into `SIGSEGV`.
- For default terminating signals, it coordinates LWP exit, core dumps, audit events, process contracts, and final `exit()`.
- Core-producing defaults are listed in `coredefault`; ignored defaults are listed in `ignoredefault`.

Disposition and child notification:
- `setsigact()` updates dispositions and related masks, clears pending ignored signals, and handles `SIGCLD` `SA_NOCLDWAIT` / `SA_NOCLDSTOP`.
- `sigdefault()` resets caught signals during exec or vfork-child setup.
- `sigcld()`, `post_sigcld()`, and `sigcld_repost()` implement serialized child-state notification so `SIGCLD` events are not lost when multiple children change state.

Signal queues:
- `sigsendproc()` and `sigsendset()` implement permission-checked signal sending over process sets.
- `sigdeq()`, `sigdelq()`, `sigcld_delete()`, `sigaddqins()`, `sigaddqa()`, and `sigaddq()` manage per-process and per-thread `sigqueue_t` lists.
- Explicitly queued signals can accumulate when `SI_CANQUEUE()` and `p_siginfo` permit it; otherwise queue depth is one per signal.
- `SIGKILL` queue metadata is stashed separately in `p_killsqp`.
- `sigqhdralloc()`, `sigqalloc()`, `sigqhdrfree()`, `sigqfree()`, `sigqrel()`, and `siginfofree()` manage bounded per-process preallocated signal queue pools.

Other interfaces:
- `stop_on_fault()` supports debugger stop-on-fault handling.
- `sigorset()`, `sigandset()`, and `sigdiffset()` are low-level kernel signal-set operations.
- `sigcheck()` tests whether a thread needs signal processing on kernel return.
- `sigintr()` and `sigunintr()` temporarily restrict interruptible signals for NFS/UFS-style interruptible mount operations.
- `sigreplace()` swaps a thread signal mask.
- `sigwillqueue()` identifies queue-capable signal codes.
- `trapsig()` posts synchronous hardware/trap signals.
- `realsigprof()` chooses slow traced or fast direct `SIGPROF` delivery.
- `siginfo_kto32()` and `siginfo_32tok()` translate native kernel `siginfo` to/from 32-bit ABI structures.

Locking model:
- Most process signal state is protected by `p_lock`.
- Parent/child notification uses `pidlock`.
- Thread state transitions use `thread_lock()`.
- Several routines deliberately drop and reacquire locks around operations that can sleep, notify `/proc`, allocate memory, or switch thread state.

Filesystem relevance:
- This is process-control infrastructure, but filesystem code depends on it for interruptible blocking operations, especially NFS/UFS paths using `sigintr()` / `sigunintr()`, syscall interruption, cancellation, and signal-driven wakeups from sleeps.
