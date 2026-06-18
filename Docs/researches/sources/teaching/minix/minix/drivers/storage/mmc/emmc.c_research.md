# File Research: sources/teaching/minix/minix/drivers/storage/mmc/emmc.c

## Purpose

Provides a dedicated AM335x/BeagleBone Black eMMC host implementation for the generic MINIX MMC block driver. It initializes MMC1, identifies and configures an eMMC card, and performs single-block read/write I/O through MMCHS registers.

## Main Entry Points

- `host_initialize_host_structure_mmchs()`: registers the eMMC host callbacks used by `mmcblk.c`.
- `emmc_host_init()`: validates BBB hardware, maps AM335x MMC1 registers, configures voltage, clocks, timeouts, interrupts, and MMCHS block length.
- `emmc_card_initialize()`: performs the eMMC initialization sequence and fills `slot->card`.
- `emmc_read()` / `emmc_write()`: read/write logical blocks through single-block commands.
- `send_cmd()` / `send_cmd_check_r1()`: low-level command submission and response validation.
- `read_data()` / `write_data()` / `read_busy()`: interrupt-driven data/busy transfer helpers.
- `cim_read_block()` / `cim_write_block()`: command-plus-data single-block operations.

## Control Flow And State

The host maps AM335x MMC1 registers, mutates the `regs_v1` offset table into virtual addresses, registers IRQ 28, and configures pins GPMC_AD4-7 for 8-bit mode when possible. Initialization resets MMCHS, powers the bus, starts at 400 kHz, enables clocks, sets auto-idle, programs 512-byte blocks, and enables command/data interrupts.

Card initialization sends CMD0, switches command line open-drain, repeats CMD1 until OCR ready, reads CID/CSD, assigns RCA 2, switches push-pull, selects the card, reads EXT_CSD, derives capacity from CSD or EXT_CSD sector count, switches high-speed mode, changes clock to 24 or 48 MHz, sets 4- or 8-bit bus width, and sets 512-byte block length. The card is then exposed as one disk with partition arrays cleared.

Data I/O loops one 512-byte block at a time. For cards at or below 2 GiB, addresses are byte addresses; above that they are sector addresses. Writes are denied if CSD write-protect bits were set.

## Dependencies

Depends on AM335x MMCHS register definitions in `omap_mmc.h`, SD/MMC command/register macros in `sdmmcreg.h`, board detection, MMIO helpers, IRQ/alarm APIs, blockdriver message queueing, and the generic `mmchost.h` contract.

## Risks

The file mutates the global `regs_v1` register-offset structure into virtual addresses, so reinitialization would add the base twice unless the process starts fresh. It supports only instance 0 and BBB MMC1. Interrupt waits queue unrelated messages while waiting for hardware; wrong alarm/IRQ handling can stall the driver. The implementation uses single-block PIO, so performance is limited. Capacity/addressing and EXT_CSD byte-order assumptions are critical.
