# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_systimer.c

Implements fine-grained per-CPU system timers on top of the machine `cputimer` abstraction. Timers are MP-safe and are dispatched without the MP lock.

Key APIs:
- `systimer_intr()`
- `systimer_intr_enable()`
- `systimer_add()`
- `systimer_del()`
- `systimer_init_periodic*()`
- `systimer_adjust_periodic()`
- `systimer_init_oneshot()`
- `systimer_changed()`

Important behavior:
- `systimer_intr()` runs ready timers from the current CPU’s sorted `gd_systimerq`; if the head is not due, it reloads the one-shot CPU timer for the remaining delta.
- Timer callbacks may delete or requeue themselves. The `gd_systimer_inprog` pointer detects whether the callback left the timer alone so periodic timers can be automatically requeued.
- Periodic timers preserve phase and can use synchronization flags such as millisecond sync, 100 kHz sync, CPU offset, and half-period offset.
- `SYSTF_NONQUEUED` periodic timers avoid accumulating missed events by advancing in multiples of the period.
- `systimer_add()` inserts into the owning CPU queue. If called from a different CPU, it sends an IPI to add on the owner CPU.
- `systimer_del()` requires the owning CPU and removes queued or in-progress timers safely.
- `systimer_changed()` recalculates timers after `sys_cputimer` changes, locally and via IPIs to other CPUs.

Concurrency model:
- Uses critical sections around queue operations.
- Remote CPU operations are marshaled through `lwkt_send_ipiq()`.
- Queue ordering supports `SYSTF_FIRST` to control ordering of coincident events.

Filesystem relevance:
- Provides the precision timer substrate used by kernel subsystems. Filesystems and VFS code indirectly depend on this through callouts, sleeps, timeouts, and periodic maintenance paths.
