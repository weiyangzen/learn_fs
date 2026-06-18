# File Research: sources/windows/winbtrfs/src/crc32c.h

## Role

`crc32c.h` is the small public declaration header for the WinBtrfs CRC32C implementation.

## API

- Declares `calc_crc32c_hw` only for `_X86_`, `_AMD64_`, or `_ARM64_`.
- Declares `calc_crc32c_sw` for all builds.
- Defines `crc_func` as a `__stdcall` function pointer taking seed, byte buffer, and length.
- Declares the global dispatch pointer `extern crc_func calc_crc32c`.
- Wraps declarations in `extern "C"` for C++ consumers.

## Dependencies

- Includes `<stdint.h>`.
- Implemented by `crc32c.c` and architecture assembly files.
- Included by `calcthread.c` and other checksum users.

## Research Notes

- This header deliberately exposes both direct implementations and the dispatch pointer. Normal callers use `calc_crc32c`; CPU feature setup code can assign it to the hardware implementation.
- The fixed `__stdcall` signature keeps x86 symbol decoration and cross-language linkage predictable.
