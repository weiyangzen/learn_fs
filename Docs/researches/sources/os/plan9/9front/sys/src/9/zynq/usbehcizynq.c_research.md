# File Research: sources/os/plan9/9front/sys/src/9/zynq/usbehcizynq.c

Implements Zynq-specific EHCI host-controller registration and reset glue.

Key responsibilities:
- Defines Zynq USB mode, OTG, and ULPI register offsets.
- Registers two possible controllers, `USB0_BASE/USB0IRQ` and `USB1_BASE/USB1IRQ`.
- `ehcireset` stops the controller, performs host-controller reset, sets interrupt threshold, and determines frame-list size.
- Supplies allocator callbacks: descriptors from uncached memory via `ucalloc`, DMA buffers via aligned `mallocalign`.
- Wraps EHCI `portstatus` to derive high/low speed from Zynq port status bits.
- `reset` claims an inactive controller, maps registers, sets host mode, configures ULPI, initializes shared EHCI memory/linkage, hooks `portstatus`, and enables interrupts.
- `usbehcilink` registers this implementation as HCI type `"ehci"`.

Notable details:
- `ctlrs` has room for three entries but only two initialized controllers; the zero base sentinel terminates scans.
