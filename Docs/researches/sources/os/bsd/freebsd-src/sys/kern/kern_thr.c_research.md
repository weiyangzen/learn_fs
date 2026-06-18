# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_thr.c

Read status: complete file reviewed.

This file implements the FreeBSD user-visible thread/LWP syscall layer: creating user threads, exiting threads, per-thread signaling, suspend/wake primitives, thread naming, and per-process thread allocation limits.

Sysctls under `kern.threads` expose `max_threads_per_proc` and `max_threads_hits`. `kern_thr_alloc` enforces the per-process thread cap before calling the lower-level allocator from `kern_thread.c`.

Thread creation is exposed through `sys_thr_create`, `sys_thr_new`, `kern_thr_new`, and `thread_create`. `thr_create` copies in a full `ucontext_t`, writes the child TID if requested, and installs the machine context. `thr_new` copies `struct thr_param`, validates flags, optionally copies realtime priority parameters, KTRACE-logs the parameter, writes child/parent TIDs, sets the user upcall stack/start function/argument, and installs TLS.

`thread_create` performs the shared creation path. It validates realtime scheduling privilege and priority, charges RACCT `RACCT_NTHR`, allocates a new thread, copies selected thread state from the caller, shares COW credentials/limits, copies machine thread state, invokes the caller-provided initializer, links the thread into the process, marks `P_HADTHREADS`, names it from `p_comm`, calls scheduler fork hooks, handles process stop/ptrace birth flags, invokes PMC/HWT hooks, inserts the TID hash entry, applies realtime priority if requested, and schedules it runnable. Failure paths unwind COW state, thread memory, and RACCT charge.

Exit paths include `sys_thr_exit` and `kern_thr_exit`. The syscall notifies umtx state, optionally stores a user wake flag and wakes waiters, then enters kernel thread exit. `kern_thr_exit` clears kernel ASTs, detects the last live/pending-exit thread and returns so userland trampoline can terminate the whole process, calls ABI thread-exit hooks, reports ptrace LWP exit if needed, removes the thread from the TID hash, subtracts RACCT thread count, cleans pending signals, audits syscall exit, marks the process stopped, and calls `thread_exit`.

Signal syscalls include `sys_thr_kill` for current-process TIDs and `sys_thr_kill2` for arbitrary process/TID pairs. They construct SI_LWP ksiginfo, validate signals, use `tdfind`/`pfind`, enforce `p_cansignal` for cross-process signaling, support signal 0 existence checks, and can broadcast to all other threads when id is -1.

Suspend/wake APIs implement libthr blocking. `kern_thr_suspend` handles optional relative timeout, pending wake flags, `msleep` on the thread under the proc lock, and maps timeout/restart results. `sys_thr_wake` either records a self-wakeup flag or locates another thread, sets `TDF_THRWAKEUP`, and wakes it.

`sys_thr_set_name` copies a bounded user string, locates the target thread, updates `td_name`, clears scheduler cached names for KTR, and invokes PMC/HWT hooks for logging.

Risk areas are races between quick child exit and parent TID storage, last-thread detection with `p_pendingexits`, ptrace stop/drop-lock windows during thread exit, RACCT charge unwinding, signal permission checks around changing process state, and suspend/wake lost wakeups across `TDP_WAKEUP` and `TDF_THRWAKEUP`.
