# File Research: sources/os/plan9/plan9/sys/src/9/teg2/io.h

Machine I/O definitions for the Tegra2 Plan 9 port, focused mostly on PCI identity, class, BAR, and device structures.

Key contents:
- Bus encoding macros: `MKBUS`, `BUSBNO`, `BUSDNO`, `BUSFNO`, `BUSTYPE`.
- PCI config register offsets and class/subclass constants.
- `Pcidev` structure used by `pci.c` and drivers for discovered PCI devices.
- Vendor IDs and BAR bit definitions.
- `PCIWADDR` translation macro for PCI windows.

Notes:
- Provides shared ABI between PCI probing, device drivers, and formatted `%T` bus identifiers.
