# File Research: sources/os/plan9/plan9/sys/src/9/mtx/pci.c

Implements generic PCI configuration, scanning, bridge discovery, BAR sizing, address assignment, and utility APIs for the MTX port.

Key points:
- Supports PCI configuration mechanisms 1 and 2 via x86-style config I/O ports (`0xCF8`, `0xCFC`, `0xCFA`) exposed through the MTX I/O path.
- Installs `%T` formatting for Plan 9 TBDF bus identifiers.
- `pcibarsize()` probes BAR size by writing all ones and restoring the original BAR.
- `pcibusmap()` recursively sizes and assigns I/O and memory windows, including PCI-PCI bridge windows, with minimum bridge window sizes and sorted allocation tables.
- `pcilscan()` enumerates devices/functions, fills `Pcidev`, reads class/vendor/device/interrupt/BAR information, detects multifunction devices, and recursively scans PCI-PCI bridges.
- `pcicfginit()` detects config mechanism, applies optional `*pcimaxbno` and `*pcimaxdno`, scans buses, resets CardBus bridges, computes top-level window sizes, then writes assigned mappings.
- Provides config read/write APIs for 8/16/32-bit registers: `pcicfgr*()` and `pcicfgw*()`.
- Provides lookup and control helpers: `pcimatch()`, `pcimatchtbdf()`, `pciipin()`, `pcihinv()`, `pcireset()`, `pcisetbme()`, and `pciclrbme()`.
- Keeps a debug ring in `PCICONS` and prints it during PCI inventory.

Dependencies and interactions:
- `raven.c` uses `pcimatch()` to locate Raven PCI registers and derive MPIC base.
- Ethernet and other PCI device drivers use `pcimatch*()` and config accessors.
- `getconf()` from `main.c` controls scan bounds.
- Uses Plan 9 `Pcidev`/`Pcisiz` structures from platform headers.

Research relevance:
- This is the PCI bus substrate for the MTX kernel, including bridge resource allocation rather than relying on firmware.
