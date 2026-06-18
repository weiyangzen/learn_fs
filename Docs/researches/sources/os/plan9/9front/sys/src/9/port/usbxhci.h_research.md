# File Research: sources/os/plan9/9front/sys/src/9/port/usbxhci.h

Small shared interface for xHCI controller glue.

Key responsibilities:
- Declares `struct Xhci`, the machine/bus-independent xHCI controller wrapper containing MMIO base, physical base/size, auxiliary bus state, DMA enable/address callbacks, and active `Hci`.
- Declares `xhcialloc()`, `xhcilinkage()`, `xhciinit()`, and `xhcishutdown()` for bus-specific front-ends.

Dependencies:
- Assumes Plan 9 kernel integer types and the generic USB `Hci` type are already visible.

Notable behavior:
- The header keeps PCI-specific policy out of the core driver by representing bus operations as callbacks.
