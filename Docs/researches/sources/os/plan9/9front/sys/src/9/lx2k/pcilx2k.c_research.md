# File Research: sources/os/plan9/9front/sys/src/9/lx2k/pcilx2k.c

LX2K PCIe root-complex driver for two DesignWare PCIe controllers. It defines controller address windows, DBI/config/I/O/memory bases, IRQ ranges, iATU register programming, config-space accessors, interrupt fanout, and root bridge initialization.

`rootinit` disables iATUs, maps config space, enables DBI read-only writes, programs bridge bus numbers/class/command/BARs, scans PCI buses, initializes INTx interrupt handlers, configures outbound I/O and memory iATUs, maps bus resources, and prints inventory.

Config reads/writes use DBI before parent device discovery and iATU CFG0/CFG1 windows after. PCI interrupts are collected into fixed vector slots and invoked by shared controller IRQ handlers; MSI is disabled for devices before installing handlers.

Notable risks: interrupt dispatch calls every registered vector on each PCI interrupt without device-specific status filtering; `pciintrenable` removes prior slots by device pointer; controller address ranges are hard-coded.
