# File Research: sources/os/plan9/9front/sys/src/9/bcm64/pcibcm.c

BCM2711 PCIe root complex and MSI support.

Key responsibilities:
- Implements Plan 9 PCI config-space read/write helpers.
- Programs root-complex memory windows and BAR mappings.
- Initializes MSI target address/data and dispatches MSI vectors.
- Provides `pciintrenable()`/`pciintrdisable()` for PCI devices using MSI.
- Scans and maps PCI bus resources.
- Brings PCIe PHY/root complex out of reset and forces Gen2 link settings.

Important behavior:
- Supports 32 MSI ISR slots.
- Allows `*pciwin` and `*pcidmawin` configuration overrides.
- Aborts PCI initialization if link status indicates PHY link down.

Dependencies:
- Plan 9 PCI core, GIC interrupt enable path, SoC PCI window settings, and BCMSTB PCIe registers.
