# File Research: sources/os/plan9/9front/sys/src/9/xen/etherxen.c

Xen virtual network interface frontend.

Purpose:
- Implements an `ether` driver named `xen` for Xen VIF devices.

Key behavior:
- Discovers VIFs through xenstore `device/vif/N`.
- Allocates shared TX/RX rings, grant references, event channel, TX frame pool, and RX frame pages.
- Publishes ring refs and event-channel to xenstore, requests rx-copy when backend supports it, and waits for backend `Connected`.
- `etherxenproc` drains outbound queue into TX grant frames.
- Interrupt handler processes RX and TX responses, recycles frames, re-posts RX buffers, and wakes transmit waiters.
- Supports control command `ea` to set Ethernet address and exposes interface stats.

Integration:
- Uses xenstore, grant-table helpers, event channels, Plan 9 `etherif`, and network block queues.

Risks/notes:
- Comments flag missing ID validation, checksum handling, and fixed speed reporting.
- `pnp` calls `intrenable` with `irq=-1` before attach also allocates a real event channel, which is notable and depends on Xen interrupt code tolerance.
