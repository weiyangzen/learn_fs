# File Research: sources/os/plan9/plan9/sys/src/9/pc/etherwavelan.c

Bus attachment glue for the WaveLAN/Prism wireless Ethernet driver. The hardware operations and core protocol logic live in `wavelan.h` and functions such as `wavelanreset()` and `w_option()`; this file provides PCMCIA and PCI reset/probe paths and registers `"wavelan"` and `"wavelanpci"`.

`wavelanpcmciareset()` allocates a `Ctlr`, sets default I/O base and IRQ when unspecified, reserves I/O ports, locates a PCMCIA card either from explicit `id=` option or by trying names from `wavenames`, calls `wavelanreset()`, then converts option strings from `key=value` to `key value` form and passes them to `w_option()`. On failure it frees I/O and controller state and clears `ether->ctlr`.

The PCI path recognizes two vendor/device pairs: Intersil Prism2.5 `1260:3873` and Linksys WPC-11 `1737:0019` marked untested. `wavelanpciscan()` scans PCI, requires BAR0 MMIO size 4096, maps the register window with `vmap`, stores the PCI device and mapped memory in a controller list, and enables bus mastering.

`wavelanpcireset()` selects an inactive PCI controller, fills IRQ/TBDF, performs a hard reset through `WR_PciCor` with delays and busy polling, calls shared `wavelanreset()`, then applies options with `w_option()`. It does not reserve I/O ports because PCI uses mapped MMIO.

Notable risks: this file assumes external definitions from `wavelan.h` for `Ctlr`, defaults, register access, and reset/option behavior. The Linksys PCI ID is explicitly untested. Option parsing mutates `ether->opt[]` strings in place by replacing `=` with space.
