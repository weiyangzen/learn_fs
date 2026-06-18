# File Research: sources/os/plan9/9front/sys/src/9/kw/usbehci.h

Kirkwood-specific EHCI header overriding generic USB debug macros and defining EHCI capability, operational, debug-port, polling, and controller structures. It contains register bits for EHCI command/status/interrupt/config/port/debug fields plus the Kirkwood/Freescale-flavored operational register layout.

`Ctlr` is the platform-private state used by generic EHCI code: capability/operational register pointers, DMA allocators, frame list, async/periodic queue heads, isochronous state, interrupt counters, and polling rendezvous state.

The `Eopio` layout includes standard EHCI registers, Kirkwood OTG/device endpoint registers, and Freescale-style snoop/priority/system interface registers.

Notable risks: comments say some Kirkwood registers are undocumented publicly and may now be standard; this header is tightly coupled to the generic EHCI implementation's expected private structures.
