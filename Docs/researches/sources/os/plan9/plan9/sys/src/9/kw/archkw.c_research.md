# File Research: sources/os/plan9/plan9/sys/src/9/kw/archkw.c

## Purpose
Contains Marvell Kirkwood/SheevaPlug platform-specific setup: SoC register base addresses, CPU address window repair, cache discovery, L2 cache enablement, GPIO reset setup, clock/power gating, reboot, Ethernet discovery, and flash discovery.

## Main Data Structures
- `GpioReg`, `L2uncache`, `Dramctl`, `Addrmap`: memory-mapped Kirkwood register layouts.
- `soc`: global `Soc` register map for CPU, interrupt controller, NAND, crypto, EHCI, SPI, TWSI, RTC, clock, Ethernet, SATA, UART, and GPIO controllers.

## Initialization Flow
- `archreset` runs early: disables watchdog, configures GPIO outputs for LEDs/USB power, enables CPU clocks, marks L2 as present, adjusts DRAM control, and applies an analog register guideline.
- `archconfinit` runs later: sets CPU frequency/delay loop, repairs address maps, optionally prints windows, prints cache configuration, and enables L2 cache.
- `fixaddrmap` scans CPU windows and enables/remaps the crypto SRAM target to `PHYSCESASRAM`, then verifies the device internal base address.
- `cacheinfo`, `prcache`, and `prcachecfg` read CP15 cache type data and derive cache size, associativity, sets, and line size.
- `l2cacheon` follows Marvell guidelines for cache lockdown, L2 config, timing, uncached windows, writeback/write-through choice, and final L1/L2 enable.

## Platform Services
- `archether` reports up to two Ethernet controllers as type `88e1116`.
- `archreboot` requests a soft reset through CPU reset registers, then waits.
- `archconsole` is currently effectively disabled/commented.
- `archflashreset` exposes NAND flash at detected physical locations for `devflash`.
- `archflashwp` is a stub.

## Dependencies and Integration
Integrates with CP15 helpers, cache maintenance, Kirkwood `io.h` constants, Ethernet and flash device layers, clock shutdown, and global `soc`.

## Risks and Notes
Most behavior is hardware-guideline-specific. The L2 uncached window disables caching for the upper half of physical address space to avoid caching I/O registers. Debug printing is compiled but disabled by `Debug = 0`.
