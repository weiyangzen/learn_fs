# File Research: sources/os/plan9/9front/sys/src/9/kw/archkw.c

Implements Marvell Kirkwood/SheevaPlug platform setup.

Key elements:
- Defines SoC register base addresses in global `soc`.
- Fixes CPU address-map windows, especially crypto SRAM mapping.
- Reads and reports L1 cache configuration.
- Enables/configures L2 cache, writeback policy, prefetch/ECC bits, and uncached upper address window.
- Initializes CPU frequency, cycle frequency, delay loop, cache info, and L2 cache.
- Performs early reset-time GPIO, clock-gate, L2, SDRAM, and analog setup.
- Provides soft reset/reboot handling.
- Exposes flash reset/probe metadata for NAND.

Dependencies:
- Uses Kirkwood register definitions from `io.h`, ARM coprocessor helpers, cache/TLB assembly helpers, and flash interfaces.

Research notes:
- The code is specific to Marvell Kirkwood systems such as SheevaPlug/OpenRD.
- It assumes a 1.2 GHz ARM926EJ-S processor and platform-specific U-Boot address mappings.
