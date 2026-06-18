# File Research: sources/os/plan9/9front/sys/src/9/imx8/pciimx.c

Role: i.MX8 PCIe root-complex driver for two DesignWare PCIe controllers, config-space access, iATU windows, and MSI dispatch.

Key responsibilities:
- Describes two controllers with memory/config/I/O windows, bus ranges, IRQ bases, and DBI MMIO bases.
- Disables and configures iATU outbound regions for config, I/O, and memory transactions.
- Maps `tbdf` to controller and returns DBI or config-window addresses for 8/16/32-bit config reads/writes.
- Maintains 32 MSI vectors per controller, using a static `msimsg` target address.
- Initializes MSI controller registers, target address, status/mask/enable, and GIC interrupt lines.
- `pciintrenable()` finds device, disables old MSI state, assigns a vector slot, enables controller bit, and programs device MSI.
- `pciintrdisable()` removes matching vector callbacks.
- `rootinit()` maps config space, enables DBI RO writes, sets bridge bus numbers/command/class, scans the bus, initializes MSI, maps I/O/memory windows, assigns resources, and prints hierarchy.
- `pciimxlink()` resets/powers/configures both PCIe blocks, configures reset GPIOs, GPRs, clock rates/gates, releases resets, scans config, and applies QoS magic.

Dependencies:
- Uses Plan 9 PCI framework, `vmap`, `pciscan`, `pcibusmap`, `pcimsienable`, `pcimsidisable`, `iomuxpad`, `iomuxgpr`, `gpioout`, `powerup`, CCM, and GIC.

Notes and risks:
- `qosmagic()` writes undocumented QoS registers to avoid LCDIF/PCIe interference.
- PCIe reset GPIOs are board-specific (`gpio5_io07`, `gpio3_io23`).
