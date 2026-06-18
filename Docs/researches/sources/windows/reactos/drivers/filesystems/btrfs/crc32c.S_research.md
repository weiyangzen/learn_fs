# File Research: sources/windows/reactos/drivers/filesystems/btrfs/crc32c.S

## Purpose

Assembly implementations of CRC32C for x86 and x86-64 builds. Provides both software table-driven CRC32C and hardware-accelerated CRC32C using the CPU `crc32` instruction.

## Main Contents

- Includes `asm.inc`.
- x86-64 section under `__x86_64__`:
  - Extern `crctable`.
  - Exports `calc_crc32c_sw`.
  - Exports `calc_crc32c_hw`.
- x86 section under `_X86_`:
  - Extern `_crctable`.
  - Exports `_calc_crc32c_sw@12`.
  - Exports `_calc_crc32c_hw@12`.

## Behavior

Software implementation:

- Starts with caller-provided seed.
- For each byte:
  - Shifts current CRC right by 8.
  - XORs low CRC byte with input byte.
  - Uses the result as an index into `crctable`.
  - XORs table value with shifted CRC.
- Returns the updated CRC.

Hardware implementation:

- Starts with caller-provided seed.
- Processes the buffer in the widest supported chunks:
  - x86-64: 8-byte chunks, then 4-byte, 2-byte, and 1-byte stragglers.
  - x86: 4-byte chunks, then 2-byte and 1-byte stragglers.
- Uses the SSE4.2 `crc32` instruction.
- Returns the updated CRC.

## Dependencies

- The CRC table is defined in `crc32c.c`.
- Function declarations are in `crc32c.h`.
- The active function pointer `calc_crc32c` is defined in `crc32c.c` and consumed by checksum code such as `calcthread.c`.

## Research Notes

- This file supplies x86/x64 implementations only. Non-x86 architectures use the C fallback in `crc32c.c`.
- Hardware acceleration is implemented here but selection of `calc_crc32c_hw` is not performed in this file.
- Calling conventions are explicitly handled: Windows x64 register convention and x86 stdcall decorated exports.
