# File Research: sources/windows/winbtrfs/src/crc32c-gas.S

## Role

`crc32c-gas.S` provides GNU assembler CRC32C implementations for x86-64 and x86 builds.

## x86-64 Path

- Exports `calc_crc32c_sw` and `calc_crc32c_hw`.
- Uses Windows x64 register arguments:
  - `rcx`: seed.
  - `rdx`: buffer.
  - `r8`: length.
- Software path:
  - Processes one byte at a time.
  - Uses external `crctable`.
  - Computes `crctable[(crc ^ byte) & 0xff] ^ (crc >> 8)`.
- Hardware path:
  - Uses SSE4.2 `crc32` instructions.
  - Processes 8-byte chunks, then 4-byte, 2-byte, and 1-byte tails.

## x86 Path

- Exports stdcall-decorated `_calc_crc32c_sw@12` and `_calc_crc32c_hw@12`.
- Reads seed, buffer, and length from stack.
- Software path mirrors the table-driven byte loop.
- Hardware path processes 4-byte chunks, then 2-byte and 1-byte tails with `crc32`.
- Returns with `ret 12`, matching stdcall cleanup.

## Dependencies

- Depends on external `crctable`/`_crctable` defined in `crc32c.c`.
- Declared by `crc32c.h` for `_X86_` and `_AMD64_`.
- Intended for non-MSVC toolchains using GAS-compatible assembly.

## Research Notes

- The file uses Intel syntax under GAS (`.intel_syntax noprefix`) to keep instruction bodies close to the MASM version.
- Hardware use must be gated by runtime CPU feature checks elsewhere; the assembly itself assumes the `crc32` instruction is available when called.
