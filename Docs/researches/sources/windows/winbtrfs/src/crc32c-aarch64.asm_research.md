# File Research: sources/windows/winbtrfs/src/crc32c-aarch64.asm

## Role

`crc32c-aarch64.asm` provides the ARM64 hardware CRC32C implementation of `calc_crc32c_hw`.

## Behavior

- Exports `calc_crc32c_hw`.
- Calling convention documented in comments:
  - `w0`: seed/current CRC.
  - `x1`: input buffer.
  - `w2`: input length.
  - `x3`: scratch.
- Processes 8-byte chunks with `crc32cx`.
- Processes remaining 4-byte, 2-byte, and 1-byte tail data with `crc32cw`, `crc32ch`, and `crc32cb`.
- Returns the updated CRC in `w0`.

## Dependencies

- Declared by `crc32c.h` when `_ARM64_` is defined.
- Selected at runtime by driver initialization when ARM64 CRC32 instructions are detected.

## Research Notes

- This file contains only the hardware path. The portable software fallback for ARM64 comes from `crc32c.c`.
- The file uses ARM assembler syntax with `AREA`, `GLOBAL`, and `END`.
- The loop branches back to `calc_crc32c_hw` for 8-byte chunks, then falls through the tail handlers.
