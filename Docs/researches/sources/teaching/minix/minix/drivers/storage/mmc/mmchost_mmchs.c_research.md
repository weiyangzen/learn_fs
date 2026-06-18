# File Research: sources/teaching/minix/minix/drivers/storage/mmc/mmchost_mmchs.c

## Purpose

Implements a general OMAP MMCHS SD-card host driver for BeagleBoard-family hardware, backing the generic MMC block driver.

## Main Entry Points

- `host_initialize_host_structure_mmchs()`: selects board-specific MMCHS instance and fills host callbacks.
- `mmchs_init()`: maps MMCHS registers, resets/configures the controller, powers the bus, sets clocks, sends the initialization stream, and registers IRQs.
- `mmc_send_cmd()` / `mmchs_send_cmd()`: translate generic `mmc_command` descriptors into MMCHS register commands.
- `intr_wait()`, `handle_bwr()`, `handle_brr()`: wait for command/data interrupts and move PIO data through the DATA register.
- `mmchs_card_initialize()`: performs SD card identification and configuration.
- `mmchs_host_read()` / `mmchs_host_write()`: perform single-block reads/writes.
- `card_goto_idle_state()`, `card_identification()`, `card_query_voltage_and_type()`, `card_identify()`, `card_csd()`, `select_card()`, `card_scr()`: SD initialization command steps.
- `enable_4bit_mode()` / `enable_high_speed_mode()`: configure bus width and clock.

## Control Flow And State

Board selection picks either BeagleBone or BeagleBoard-xM register base/IRQ and register layout. `mmchs_init()` grants memory access, maps registers, soft-resets, advertises capabilities, configures power/idle/wakeup, starts at 400 kHz, enables interrupts, sends an init stream, sets data timeout, and enables interrupt signaling.

Command submission writes ARG/CMD, waits for command completion, handles optional data transfers through global `io_data`/`io_len`, and copies responses from MMCHS response registers. SD initialization sends CMD0, CMD8, ACMD41 loops, CMD2, CMD3, CMD9, CMD7, ACMD51, ACMD6, and speed selection based on CSD. The card is exposed as a 512-byte-block disk with size from CSD v2 capacity.

## Dependencies

Depends on `mmchost.h`, `sdmmcreg.h`, `sdhcreg.h`, `omap_mmc.h`, MINIX MMIO, board detection, VM physical mapping, IRQ/alarm APIs, and blockdriver message queueing.

## Risks

The code uses globals for current controller and current data buffer, so concurrent requests would need external serialization. `intr_wait()` queues unrelated messages while waiting but has complex reenable/timeout paths. Several host read/write helpers ignore command failure return values and return `OK`. Only SDHC-like CSD version 2.0 cards are accepted. Card detection is a stub that always reports present.
