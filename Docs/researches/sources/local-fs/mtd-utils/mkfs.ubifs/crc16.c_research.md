# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/crc16.c

## Purpose
Provides a table-driven CRC-16 implementation used by UBIFS LPT node packing.

## Main Data and Entry Point
- `crc16_table[256]` is the lookup table for the standard CRC-16 polynomial `0x8005`.
- `crc16()` updates a supplied CRC over a byte buffer using `crc16_byte()`.

## Dependencies
Includes `crc16.h`; the code notes that it was taken from the Linux kernel under GPLv2.

## Risks and Notes
The function is incremental: callers supply the initial or previous CRC value. LPT code uses an initial value of `-1`, relying on truncation to `uint16_t`.
