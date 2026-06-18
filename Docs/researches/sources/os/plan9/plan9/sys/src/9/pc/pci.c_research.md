# File Research: sources/os/plan9/plan9/sys/src/9/pc/pci.c

PC PCI enumeration, config-space access, BAR sizing/resource assignment, BIOS routing, device matching, reset, and power-management support.

Key elements:
- Supports PCI config mechanisms 1 and 2, plus optional BIOS32 PCI service access.
- `pcicfginit` detects config mode, scans buses, optionally uses BIOS32, applies `*pcimaxbno`, `*pcimaxdno`, `*nobios`, `*pcibios`, `*nopcirouting`, and optionally prints inventory.
- `pcilscan` enumerates devices/functions, reads IDs/class/header/BARs, detects multifunction devices, recursively scans PCI-PCI bridges, and sets `pcivga`.
- `pcibarsize` probes BAR sizes by writing all ones and restoring the original value.
- `pcibusmap` assigns I/O and memory resources when firmware did not.
- `$PIR` routing support scans BIOS memory, matches known southbridges, and fixes PCI interrupt line registers.
- Raw and BIOS config accessors back public `pcicfgr8/16/32` and `pcicfgw8/16/32`.
- `pcimatch`, `pcimatchtbdf`, `pciipin` provide device lookup.
- `pcireservemem` reserves memory BAR ranges from the UPA allocator.
- `pcihinv` prints PCI inventory.
- `pcireset` clears bus mastering for non-bridge devices.
- Command helpers set/clear I/O enable, bus master enable, and memory-write-invalidate.
- `pcigetpms`, `pcisetpms` walk PCI capabilities for standard power management state.

Interactions:
- Storage driver `sd53c8xx.c`, SMBus driver `piix4smbus.c`, VGA code, and MP interrupt routing all depend on PCI lookup/config helpers.
- Uses `upareserve` from `memory.c` to protect BAR physical ranges.

Research notes:
- Foundational for block/storage hardware discovery in this subset.
- File comment says it needs a rewrite; code mixes enumeration, resource allocation, IRQ routing, and power management.
