# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/crc16.h

## Purpose
Declares CRC-16 table/function symbols and provides the inline one-byte update helper.

## Main Definitions
- `extern uint16_t const crc16_table[256]`.
- `extern uint16_t crc16(uint16_t crc, const uint8_t *buffer, size_t len)`.
- `crc16_byte()` performs one lookup-table update.

## Dependencies
Includes `<stdlib.h>` for `size_t` and `<stdint.h>` for fixed-width integer types.

## Risks and Notes
The implementation assumes callers use the same CRC initialization convention as the UBIFS/JFFS code paths that consume it.
