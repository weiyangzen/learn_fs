# File Research: sources/teaching/minix/minix/drivers/storage/mmc/sdmmcreg.h

## Purpose

Provides NetBSD/OpenBSD-derived MMC and SD command numbers, OCR/R1/CSD/CID/SCR/EXT_CSD bit definitions, response decoding macros, and a bitfield extraction helper.

## API Surface

Defines MMC commands, SD commands, SD application commands, OCR voltage/capacity bits, R1 status bits, RCA helpers, EXT_CSD fields and bus-width values, SPI status bits, CSD/CID/SCR field extraction macros, SDHC capacity decoding, speed constants, and `MMC_RSP_BITS()` backed by `__bitfield()`.

## Dependencies

Used by eMMC, MMCHS, and dummy host implementations to build commands and interpret card register responses.

## Risks

All capacity, speed, write-protect, and bus-width decisions rely on correct bit numbering. `__bitfield()` extracts from a byte view of response words and is intentionally endian-sensitive to the response layout expected by imported code. A mismatch between host response register ordering and these macros can silently miscompute capacity or capabilities.
