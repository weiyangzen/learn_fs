# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_xcall.c

Read completely: 594 lines.

This file implements CPU cross-calls: requests to execute a function on a specific CPU or all CPUs. It provides a low-priority kthread path and a high-priority soft interrupt/IPI path.

State:
- `xc_low_pri` and `xc_high_pri` are global state boxes containing lock, condvar, current function/args, head/done tickets, and high-priority IPL.
- Per-CPU `cpu_xcall_pending` plus `cpu_xcall` condvar drives low-priority worker wakeups.
- `xc_sihs[]` stores softint handles for supported `IPL_SOFT*` levels.
- Event counters track unicast and broadcast calls.

Key functions:
- `xc_init_cpu` initializes global state once and starts one bound `xcall/N` kthread per CPU.
- `xc_broadcast` and `xc_unicast` dispatch high or low priority work and return a ticket.
- `xc_wait` waits until the ticket has completed.
- `xc_barrier` broadcasts a no-op and waits.
- `xc_lowpri` serializes one outstanding low-priority request globally and signals target CPU kthreads.
- `xc_thread` executes low-priority requests in thread context.
- `xc_highpri` publishes the request, sends IPIs or schedules local handling, and returns a high-priority ticket.
- `xc_ipi_handler` schedules the selected softint; `xc__highpri_intr` runs the function and advances completion.

Integration: cross-calls are used for per-CPU hardware/software state changes where normal locking is too expensive or impossible. The file has rump-kernel and uniprocessor fallbacks.

Reliability notes: cross-calls must not run from interrupt/soft interrupt context and must be sleepable at the caller. Low-priority calls use one global request slot, so they serialize. High-priority callbacks run in softint context and must be lightweight/nonblocking. The comments explicitly warn that cross-call functions must not allocate memory because the pagedaemon may use this facility.
