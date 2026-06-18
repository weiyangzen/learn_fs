# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_periodic.h

This private kernel header defines the implementation backing the DDI periodic handler interface. It includes list, taskq, and cyclic infrastructure.

It defines an opaque `timeout_t` for `i_timeout()` and `i_untimeout()`, periodic state flags (`DPF_DISPATCHED`, `DPF_EXECUTING`, `DPF_CANCELLED`), and `ddi_periodic_impl_t`, the in-core record for a registered periodic handler.

`ddi_periodic_impl_t` stores global and softint list links, an id, interval, lock/cv, state flags, interrupt/taskq dispatch level, taskq entry for level zero work, fire count, current executing thread, cyclic id, callback function, and callback argument.

Private lifecycle and dispatch functions are declared: `ddi_periodic_init`, `ddi_periodic_fini`, `ddi_periodic_softintr`, `i_timeout`, and `i_untimeout`.

Research notes:
- This is kernel-only implementation state, not the public `ddi_periodic_add`/remove surface.
- It bridges cyclic timers, taskq dispatch, soft interrupts, and cancellation synchronization.
