# File Research: sources/teaching/minix/minix/drivers/storage/mmc/mmcblk.c

## Purpose

Implements the generic MINIX blockdriver layer for MMC/SD cards, abstracting host-controller operations behind `struct mmc_host`.

## Main Entry Points

- `main()`: parses environment arguments, initializes SEF, and enters `blockdriver_task()`.
- `apply_env()`: selects the host driver (`mmchs` by default on ARM or `dummy`) and applies `log_level` and `instance`.
- `block_open()` / `block_close()`: detect/initialize cards, parse partitions, maintain open count, and release cards.
- `block_transfer()`: validates block-aligned iovecs and performs block-by-block read/write through host callbacks.
- `block_ioctl()`: supports `DIOCOPENCT` and `DIOCFLUSH`.
- `block_part()`: maps MINIX disk/partition/subpartition minor numbers to `struct device`.
- `get_slot()`: maps supported minors to the single supported slot.
- `hw_intr()`: forwards leftover interrupts to the host.

## Control Flow And State

The driver keeps one global `struct mmc_host host`. It supports a single card/slot exposed as disk 0 plus primary and MINIX subpartitions. On first open, it detects a card, initializes it if not already in data transfer mode, parses partitions with `partition()`, and increments `open_ct`. Subsequent opens increment `open_ct` without reinitialization. Last close calls `card_release()`.

Transfers require position and every iovec size to be multiples of the card block size, and require the block size to fit the 4 KiB `copybuff`. The code copies one block at a time between caller grants and `copybuff`, then calls `host->read()` or `host->write()` for one block. EOF truncation happens at the selected partition size.

## Dependencies

Depends on `mmchost.h`, MINIX blockdriver/drvlib/log/env APIs, safe-copy grants, partition parsing, and host implementations that fill all required callback pointers.

## Risks

The return values from `host->read()` and `host->write()` inside `block_transfer()` are ignored, so media errors may be reported as successful transfers. The driver mutates neither iovec sizes nor offsets but uses fixed `i * blk_size` offsets per iovec, so each iovec is independently handled. It only supports the first disk/slot despite structures allowing more. Signal termination refuses SIGTERM while open count is nonzero.
