# File Research: sources/windows/reactos/drivers/filesystems/btrfs/crc32c.c

## Purpose

Defines CRC32C shared state for the Btrfs driver: the exported function pointer, the 256-entry CRC32C table, and the portable C software fallback for non-x86 architectures.

## Main Contents

- Includes:
  - `crc32c.h`
  - `<stdint.h>`
  - `<stdbool.h>`
  - `<sal.h>`
- Global function pointer:
  - `crc_func calc_crc32c = calc_crc32c_sw;`
- Constant table:
  - `const uint32_t crctable[]` with 256 CRC32C values.
- Portable fallback:
  - `calc_crc32c_sw` is compiled only when neither `_X86_` nor `_AMD64_` is defined.

## Behavior

The C fallback:

- Initializes remainder from the seed.
- Iterates every byte in the input buffer.
- Updates the remainder using `crctable[(rem ^ msg[i]) & 0xff] ^ (rem >> 8)`.
- Returns the unfinalized CRC remainder.

Callers perform Btrfs-specific finalization/inversion where needed; for example `calcthread.c` stores `~calc_crc32c(0xffffffff, sector, sector_size)`.

## Dependencies

- `crc32c.S` provides x86/x64 implementations for `calc_crc32c_sw` and `calc_crc32c_hw`.
- `crc32c.h` exposes the function pointer and declarations.
- Consumers use `calc_crc32c` instead of calling a specific implementation directly.

## Research Notes

- Default implementation is software CRC32C. Hardware selection, if enabled, must occur elsewhere by assigning `calc_crc32c = calc_crc32c_hw`.
- The table is shared by the C fallback and assembly software implementation.
