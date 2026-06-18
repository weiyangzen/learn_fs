# File Research: sources/windows/winbtrfs/src/crc32c.c

## Role

`crc32c.c` defines the CRC32C function pointer, lookup table, and portable software implementation used by WinBtrfs.

## Behavior

- Defines `crc_func calc_crc32c = calc_crc32c_sw`, so the default implementation is software.
- Defines the 256-entry CRC32C table `crctable`.
- For non-x86/non-amd64 builds, defines `calc_crc32c_sw` in C:
  - Starts with the supplied seed.
  - For each byte, updates `rem = crctable[(rem ^ msg[i]) & 0xff] ^ (rem >> 8)`.
  - Returns the non-finalized remainder.

## Architecture Interaction

- x86 and amd64 software implementations live in assembly files, so the C software function is excluded for `_X86_` and `_AMD64_`.
- ARM64 gets the C software fallback here and the hardware implementation from `crc32c-aarch64.asm`.
- Driver initialization elsewhere can replace `calc_crc32c` with `calc_crc32c_hw` after CPU feature detection.
- Callers perform Btrfs-specific final inversion where needed, for example `~calc_crc32c(0xffffffff, ...)`.

## Dependencies

- Includes `crc32c.h`, standard integer/bool headers, and SAL annotations.
- The assembly files depend on this file's exported `crctable`.

## Research Notes

- The function pointer design makes hardware acceleration transparent to checksum callers.
- The implementation returns an intermediate CRC state, not always the final Btrfs checksum value; callers decide seed and complement semantics.
