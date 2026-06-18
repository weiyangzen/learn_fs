# File Research: sources/os/plan9/9front/sys/src/9/port/usbxhcipci.c

PCI attachment layer for the generic xHCI driver.

Key responsibilities:
- Scans PCI devices once for USB serial-bus xHCI controllers (`ccrb` serial, `ccru` USB, `ccrp` 0x30).
- Maps BAR0 MMIO space with `vmap()`, allocates `Xhci` wrappers, records the backing `Pcidev`, and installs PCI DMA helpers.
- Enables bus mastering through `pcisetbme()` and translates DMA addresses with `PCIWADDR()`.
- Implements `reset()` for `addhcitype("xhci", reset)`, honoring `*nousbxhci`, matching optional requested port addresses, and wiring IRQ/TBDF/linkage into `Hci`.
- Wraps core init/shutdown with `pcienable()`/`pcidisable()`.

Dependencies:
- Uses Plan 9 PCI discovery/configuration, virtual mapping, and generic USB HCI registration.

Notable behavior:
- Controllers are cached in a fixed `ctlrs[Nhcis]` table and selected only if not already active.
