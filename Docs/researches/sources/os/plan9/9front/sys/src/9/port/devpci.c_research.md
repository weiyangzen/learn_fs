# File Research: sources/os/plan9/9front/sys/src/9/port/devpci.c

Purpose: Provides a stripped-down PCI-only `#$` device for enumerating PCI devices and reading/writing PCI configuration space.

Key logic:
- Exposes top directory `pci`, then per-device `bus.dev.fnctl` and `bus.dev.fnraw` files.
- `pcidirgen` enumerates PCI devices with `pcimatch` and resolves qids back to devices with `pcimatchtbdf`.
- `ctl` reads summarize class codes, vendor/device IDs, interrupt line, and populated BARs.
- `raw` reads and writes the first 256 bytes of PCI config space, using aligned 32-bit/16-bit accesses when possible and byte accesses otherwise.

Dependencies and integration:
- Depends on `../port/pci.h`, `Pcidev`, `pcimatch`, `pcimatchtbdf`, `pcicfgr*`, and `pcicfgw*`.

Risks and notes:
- Raw writes directly mutate PCI config registers and are exposed with `0660` permissions.
- This file intentionally duplicates only the PCI subset of the larger ISA PNP plus PCI device.
