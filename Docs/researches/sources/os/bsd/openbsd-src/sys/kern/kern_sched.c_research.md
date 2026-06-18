# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_sched.c

Purpose: Implements per-CPU run queues, CPU selection, idle threads, process switching support, CPU sets, CPU hot/online controls, and scheduler barriers.

Key behavior:
- `sched_init()` and `sched_init_cpu()` initialize CPU sets, run queues, per-CPU clock interrupts, dead process lists, and SMR deferred queues.
- `sched_kthreads_create()` creates one idle thread per CPU.
- `sched_idle()` runs the idle loop, handles dead process cleanup, calls `smr_idle()`, enters/leaves idle CPU sets, and cooperates with CPU halt flags.
- `sched_exit()` moves dead threads to the local CPU dead list and switches to idle.
- `sched_toidle()` cancels per-thread timers, releases the kernel lock on MP, and switches directly to the CPU idle process.

Run queue logic:
- `setrunqueue()` chooses a CPU when needed, updates priority/run state, enqueues, marks queued CPU sets, wakes idle CPUs, and requests reschedule on priority preemption.
- `remrunqueue()` removes queued threads and updates per-CPU queue masks.
- `sched_chooseproc()` selects the highest-priority local runnable thread, steals from other CPUs, or runs idle.
- `sched_choosecpu()` and `sched_choosecpu_fork()` pick CPUs based on idle/queued sets, affinity, pegging, load, primary CPU cost, and pmap residency estimate.
- `sched_steal_proc()` migrates an eligible unpegged runnable thread.

Multiprocessor controls:
- `sched_peg_curproc()` and `sched_unpeg_curproc()` temporarily bind a thread to a CPU.
- `sched_start_secondary_cpus()` and `sched_stop_secondary_cpus()` maintain schedulable CPU sets.
- `sched_barrier()` queues a task that runs on a target CPU and signals completion.
- `cpuset_*()` helpers implement basic CPU set operations and sysctl-facing CPU online counts.

Filesystem relevance:
- Filesystem code depends on scheduler sleep/wakeup, SMR quiescence, process exit cleanup, and cross-CPU barriers for safe teardown.
