# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/event_channel.h

Imported Xen public event-channel ABI.

Purpose:
- Defines Xen event-channel operations, port type, operation payloads, status values, and legacy compat wrapper.

Key content:
- Documents event channels as Xen’s notification/interrupt primitive with pending and mask bits in shared info/VCPU info.
- Defines `EVTCHNOP_*` commands: bind interdomain, bind virq, bind pirq, close, send, status, alloc unbound, bind ipi, bind vcpu, unmask, reset.
- Defines `evtchn_port_t`.
- Defines payload structures for allocation, interdomain binding, VIRQ/PIRQ/IPI binding, close, send, status, vCPU binding, unmask, and reset.
- Defines status constants for closed, unbound, interdomain, PIRQ, VIRQ, and IPI.
- Defines legacy `struct evtchn_op` for the older compat hypercall.

Integration:
- Directly used by 9front Xen event-channel allocation/notification paths in `xensystem.c`.
- Underpins xenstore, console, virtual block, and virtual network notification paths.
- `sdxen.c` and `etherxen.c` use event channels alongside rings and grant references.

Risks/notes:
- Event masking and pending-bit handling is interrupt-critical.
- Incorrect port binding or unmask behavior can cause lost device completions or stuck startup.
