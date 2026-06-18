# File Research: sources/os/plan9/plan9/sys/src/9/teg2/pci.c

Tegra2 PCI/PCIe support code for configuration-space access, device scanning, and basic PCI helpers.

Key behavior:
- Models the Tegra PCI controller register layout and memory-mapped config windows.
- Initializes controller access if the expected NVIDIA/Realtek IDs are present.
- Scans buses/devices/functions with conservative TrimSlice limits to avoid hangs.
- Builds global and tree-linked `Pcidev` lists, sizes BARs, and descends PCI bridges.
- Provides `pcimatch`, `pcimatchtbdf`, `pcihinv`, `pcireset`, config read/write wrappers, bus-master/io/mwi toggles, and PCI power-management helpers.
- Dismisses PCIe interrupt status through AFI magic register writes.

Notes:
- Comments call out that this needs a rewrite and contains board-specific assumptions.
- Bus scanning starts at bus 1 for TrimSlice.
