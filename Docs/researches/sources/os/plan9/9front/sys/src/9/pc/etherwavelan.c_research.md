# File Research: sources/os/plan9/9front/sys/src/9/pc/etherwavelan.c

Provides PCMCIA and PCI bus attachment glue for the WaveLAN/Prism wireless driver core in `wavelan.h` and related files.

Key elements:
- `wavelanpcmciareset()` allocates a `Ctlr`, applies default I/O port and IRQ values when absent, reserves I/O ports, locates a PCMCIA card either by explicit `id=` option or known `wavenames`, calls shared `wavelanreset()`, and applies remaining options with `w_option()`.
- If PCMCIA setup fails, it frees I/O space, releases the controller, clears `ether->ctlr`, and returns `-1`.
- Defines a small PCI device table for Intersil Prism2.5 `0x1260:0x3873` and an untested Linksys WPC-11 `0x1737:0x0019`.
- `wavelanpciscan()` scans matching PCI devices, validates that BAR0 is a 4 KB memory-mapped register window, maps it with `vmap()`, stores `mmb`, and chains controllers.
- `wavelanpcireset()` picks the first inactive scanned PCI controller, enables PCI, records IRQ/TBDF, performs a hard reset through `WR_PciCor`, waits for command-busy to clear, calls `wavelanreset()`, applies options, and enables bus mastering.
- `etherwavelanlink()` registers two card names: `wavelan` for PCMCIA and `wavelanpci` for PCI.

Filesystem relevance: none directly. The file is small but shows how 9front separates bus-specific discovery/reset from a shared device core and how Plan 9 Ethernet options are passed through to hardware-specific configuration.
