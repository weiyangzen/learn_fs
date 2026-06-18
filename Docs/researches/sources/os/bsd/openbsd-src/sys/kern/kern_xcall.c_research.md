# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_xcall.c

Read completely: 157 lines.

Implements cross-CPU function calls. It provides a common API for initializing an `xcall`, executing it locally at softclock IPL, queueing it to another CPU with an IPI on multiprocessor systems, synchronous cross-calls, and uniprocessor fallbacks.

Core behavior:
- `cpu_xcall_set()` stores the callback and argument in a caller-owned `struct xcall`.
- `cpu_xcall_self()` raises to `IPL_XCALL` (`IPL_SOFTCLOCK`), invokes the callback locally, and restores IPL.
- On multiprocessor kernels, `cpu_xcall()` executes immediately for the current CPU or atomically claims a slot in the target CPU's `ci_xcall.xci_xcalls[]`, sends an IPI, and busy-waits if all slots are full.
- `cpu_xcall_dispatch()` is called by machine-dependent IPI code, drains non-NULL xcall slots on the target CPU, clears each slot, and invokes callbacks.
- `cpu_xcall_establish()` initializes a CPU's xcall slots to NULL.

Synchronous calls:
- `struct xcall_sync` wraps an xcall plus a condition variable.
- `cpu_xcall_done()` runs the requested callback and signals the condition.
- `cpu_xcall_sync()` queues a wrapper xcall to the target CPU and waits on the condition variable with the provided wait message.

Uniprocessor fallback:
- `cpu_xcall()` and `cpu_xcall_sync()` simply execute the callback locally with `IPL_XCALL` raised.
- The file depends on machine-dependent `cpu_xcall_ipi()` only in the multiprocessor path.
