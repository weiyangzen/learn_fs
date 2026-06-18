# File Research: sources/teaching/minix/minix/drivers/storage/mmc/mmchost.h

## Purpose

Defines the host/card abstraction contract between `mmcblk.c` and MMC/SD host-controller implementations.

## API Surface

- Constants define partition counts, slot count, and simple card states.
- `struct sd_card_regs`: stores CID, RCA, DSR, CSD, SCR, OCR, SSR, and CSR.
- `struct mmc_command`: generic command descriptor with command, argument, response type, data direction, response buffer, and data buffer.
- `struct sd_card`: holds slot pointer, card registers, block size/count, state, open count, and MINIX partition/subpartition devices.
- `struct sd_slot`: links a host to one card.
- `struct mmc_host`: callback table for instance selection, init, log level, reset, card detection/init/release, interrupt handling, and block read/write.
- Declares `host_initialize_host_structure_mmchs()` and `host_initialize_host_structure_dummy()`.

## Dependencies

Depends on MINIX `struct device` from included driver headers through users of this header and on SD/MMC register definitions for command semantics.

## Risks

The header is the central ABI between the generic driver and hosts. Callback pointers must be fully initialized before `mmcblk.c` starts. Misspellings such as `PARTITONS_PER_DISK` are harmless internally but make the contract easy to misuse. Card states are minimal and do not model removal/error states.
