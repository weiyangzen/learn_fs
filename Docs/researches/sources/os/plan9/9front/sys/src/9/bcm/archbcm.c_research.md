# File Research: sources/os/plan9/9front/sys/src/9/bcm/archbcm.c

BCM2835/Raspberry Pi 1 board support.

Key behavior:
- Defines global `Soc` parameters for 512 MB DRAM, bus/physical/virtual I/O ranges, and cache attributes.
- Implements watchdog reset, watchdog feed, and watchdog disable.
- Enables FPU in `archreset`.
- Reports CPU as ARM1176JZF-S.
- Restricts CPU count/startup to one CPU.
- Installs watchdog feed as a clock callback.
- Implements `cmpswap` via `cas32`.

Dependencies:
- Uses power management registers at `VIRTIO + 0x100000`.

Research notes:
- This file targets the original single-core Raspberry Pi SoC.
