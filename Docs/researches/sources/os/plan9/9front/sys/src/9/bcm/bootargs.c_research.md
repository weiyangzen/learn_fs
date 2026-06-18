# File Research: sources/os/plan9/9front/sys/src/9/bcm/bootargs.c

BCM boot configuration parser for device tree, ATAGs, and reboot-saved config.

Key behavior:
- Maintains a 64-entry config table with case-insensitive keys.
- Parses newline `plan9.ini` content and command-line tokens.
- Parses flattened device tree nodes for memory, `/chosen/bootargs`, `emmc2bus` DMA ranges, and PCI host bridge memory/DMA windows.
- Parses legacy ARM ATAG memory and command-line records.
- `bootargsinit` first uses the firmware-provided DTB/ATAG physical pointer, then falls back to `CONFADDR`.
- Exposes `getconf`, `setconfenv`, and `writeconf`.

Dependencies:
- Uses kernel address conversion, firmware boot pointer, and environment helpers.

Research notes:
- More capable than the ARM64 bootargs parser because Raspberry Pi firmware may provide either DTB or ATAGs and board-specific bus windows.
