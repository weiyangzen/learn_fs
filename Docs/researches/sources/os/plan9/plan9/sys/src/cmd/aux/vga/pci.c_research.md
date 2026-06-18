# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/pci.c

Provides raw PCI configuration-space scanning and access helpers for `aux/vga`.

Key behavior:
- Detects PCI configuration mechanism 2 first, then mechanism 1, and records max device number accordingly.
- `pciscan()` walks bus/device/function space, creates `Pcidev` records, captures vendor/device/revision/class/interrupt data, and probes BAR sizes for common device classes.
- Recursively discovers PCI-PCI bridges, initializing secondary/subordinate bus numbers when firmware did not.
- Provides 8-, 16-, and 32-bit read/write helpers over both PCI config mechanisms.
- `pcimatch()` iterates the global flat PCI list by vendor/device.
- `pcihinv()` prints a hierarchical PCI inventory with class, IDs, interrupt line, and BAR data.

Important details:
- The file explicitly notes this is unsafe without locks or restrictions on what can be poked.
- BAR probing temporarily writes all ones to device registers and restores the original value.
- Bridge scanning may modify command/status and bus-number registers.
- Global state is lazily initialized and not concurrency-safe.

Filesystem relevance:
- Indirect: display drivers use this to find PCI video adapters and MMIO apertures before configuring Plan 9’s video device.
