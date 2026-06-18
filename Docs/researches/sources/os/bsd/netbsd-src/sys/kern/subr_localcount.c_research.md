# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_localcount.c

Read completely: 291 lines.

Implements `localcount(9)`, a CPU-local reference-counting scheme optimized for cheap acquire/release and expensive drain. Each object owns a percpu counter and an optional global total pointer used only while draining.

Core behavior:
- `localcount_init()` allocates the percpu counter storage.
- `localcount_acquire()` increments the current CPU's counter without interprocessor synchronization.
- `localcount_release()` normally decrements the current CPU counter; during drain it decrements the shared total under the caller-provided interlock and wakes the caller-provided CV when zero.
- `localcount_drain()` marks the object draining, broadcasts an xcall to aggregate all per-CPU counts into a stack total, then waits for the total to reach zero.
- `localcount_fini()` frees percpu storage after drain.
- DEBUG/LOCKDEBUG builds maintain a diagnostic total reference count.

Risks and notes:
- Callers must prevent new acquisitions before draining.
- The same CV and interlock must be used for drain and release.
- Release disables preemption so a racing drain cannot miss the CPU-local decrement/wakeup transition.
