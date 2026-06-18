# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_kthread.c

Read completely: 293 lines.

Implements creation, exit, join, and FPU access control for kernel threads, represented as system-only LWPs in `proc0`.

Initialization:
- `kthread_sysinit()` initializes the global mutex/CV used for join synchronization.

Creation:
- `kthread_create()` allocates a system U-area, chooses scheduling class (`SCHED_OTHER` for `KTHREAD_TS`, otherwise `SCHED_RR`), creates a detached LWP in `proc0`, optionally names it, assigns priority, optionally binds it to a CPU, sets join/intr/MPSAFE flags, and makes it runnable unless it is an idle thread.
- `KTHREAD_IDLE` can allocate the U-area on the target CPU and leaves the LWP idle rather than runnable.
- The function requires interrupt kthreads to be MPSAFE.

Exit and join:
- `kthread_exit()` drops the kernel lock for non-MPSAFE kthreads, logs nonzero exit codes, synchronizes with a joiner for `LP_MUSTJOIN` threads by waiting until `l_private` points to a joiner's stack flag, sets that flag, broadcasts, and calls `lwp_exit()`.
- `kthread_join()` asserts it is joining a system LWP marked `LP_MUSTJOIN`, stores a pointer to a stack-local `exited` flag in the target LWP's `l_private`, wakes the target, and waits until the target sets the flag. After publishing `l_private`, it must not touch the LWP because it may be freed.

FPU access:
- `kthread_fpu_enter()` asserts thread context and system-LWP context, records whether `LW_SYSTEM_FPU` was already set, sets it, and calls MD enable logic only on the outermost entry.
- `kthread_fpu_exit()` restores the previous `LW_SYSTEM_FPU` state and calls MD zero/disable logic when leaving the outermost FPU section.

Concurrency and integration:
- Creation manipulates `proc0.p_lock` and LWP scheduler locks.
- Join uses `kthread_lock`/`kthread_cv` and a stack flag handoff to avoid dereferencing the target after it may be freed.
- Integrates with UVM system U-area allocation, KMSAN origin tagging, scheduler priority/class selection, and MD FPU hooks.

Risks and notes:
- `kthread_join()` relies on the target calling `kthread_exit()`; a must-join kthread that exits another way would not complete this handshake.
- FPU enter/exit are explicitly forbidden in hard or soft interrupt context.
