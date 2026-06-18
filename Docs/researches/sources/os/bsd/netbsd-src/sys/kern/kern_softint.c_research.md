# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_softint.c

Read completely: 872 lines.

Implements NetBSD's generic software interrupt framework. It provides dynamically registered per-CPU callbacks at clock, bio, net, and serial software-interrupt levels, with both scheduler-based and architecture fast-softint dispatch paths.

Core structures:
- `softint_t` represents one interrupt level on one CPU, with a pending handler queue, backing LWP, CPU pointer, machine-dependent trigger token, event counters, active flag, IPL, and names.
- `softhand_t` stores one registered handler's function, argument, per-CPU interrupt object, flags, and optional remote-CPU IPI id.
- `softcpu_t` holds per-CPU softint state and the handler table.

Initialization and registration:
- `softint_init()` allocates per-CPU softint memory, initializes four softint LWPs per CPU, and copies established handlers from the boot CPU to later CPUs.
- `softint_init_isr()` creates the per-level interrupt LWP, attaches event counters, records IPL, and calls MD initialization.
- `softint_establish()` finds a free handler slot, optionally registers an IPI hook for `SOFTINT_RCPU`, and installs equivalent handler records on all CPUs.
- `softint_disestablish()` unregisters any IPI hook, runs an xcall barrier to ensure no handler is still executing, fires a DTrace probe, and clears the handler on all CPUs.

Scheduling and execution:
- `softint_schedule()` schedules a handler on the current CPU, requiring hardware-interrupt context or preemption disabled for stable `curcpu()`. It marks `SOFTINT_PENDING`, queues the handler, and triggers the softint if inactive.
- `softint_schedule_cpu()` schedules locally or sends an IPI to a remote CPU for handlers established with `SOFTINT_RCPU`.
- `softint_execute()` runs queued handlers FIFO at the requested softint level, drops/restores IPL around callbacks, takes the big kernel lock for non-MPSAFE handlers, emits SDT probes, and asserts no leaked spin locks, psrefs, biglocks, or preemption disables.
- `softint_block()` increments the per-level block counter when a softint LWP blocks.

Slow path without `__HAVE_FAST_SOFTINTS`:
- `softint_init_md()` makes each softint LWP runnable and records a CPU softint bit.
- `softint_trigger()` sets pending CPU bits and requests rescheduling or AST notification.
- `softint_thread()` loops running pending handlers then parks the softint LWP as idle.
- `softint_picklwp()` selects the highest-priority pending softint LWP for `mi_switch()`.

Fast path with `__HAVE_FAST_SOFTINTS`:
- `softint_thread()` must never be reached and panics.
- `softint_dispatch()` is entered by MD interrupt code, runs the softint on its dedicated LWP stack, optionally accounts interrupt time, and either returns to the pinned interrupted LWP or switches normally if the softint blocked.

Concurrency and notes:
- Handler queues are per-CPU and protected by raising IPL rather than inter-CPU locks.
- Registered handler identity is an offset within per-CPU `softcpu_t`, allowing the same handle to locate each CPU's copy.
- Softints may block briefly but must not perform long waits or resource sleeps.
