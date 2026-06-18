# File Research: sources/os/bsd/netbsd-src/sys/sys/xcall.h

Read completely: 62 lines.

Kernel-only interface for cross-calls, NetBSD's mechanism to invoke functions on other CPUs and wait for completion.

Core API:
- `xcfunc_t` is a two-argument callback.
- `XC_HIGHPRI` and `XC_HIGHPRI_IPL(ipl)` request high-priority cross-calls with encoded IPL.
- CPU bring-up/IPI hooks include `xc_init_cpu`, `xc_send_ipi`, `xc_ipi_handler`, and `xc__highpri_intr`.
- `xc_broadcast` sends to all CPUs, `xc_unicast` sends to one CPU, and both return a ticket waited on by `xc_wait`.
- `xc_barrier` provides a cross-CPU synchronization barrier.
- `xc_encode_ipl` converts IPL into cross-call flags.

Risks and notes:
- Only visible to `_KERNEL`; callbacks must be safe for the requested priority/IPL context.
