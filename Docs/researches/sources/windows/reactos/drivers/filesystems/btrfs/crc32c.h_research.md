# File Research: sources/windows/reactos/drivers/filesystems/btrfs/crc32c.h

## Purpose

Public internal header for CRC32C checksum routines used by the Btrfs driver.

## Main Contents

- Includes `<stdint.h>`.
- Provides C++ linkage guards with `extern "C"`.
- Declares `calc_crc32c_hw` on x86/x64 builds.
- Declares `calc_crc32c_sw`.
- Defines:
  - `typedef uint32_t (__stdcall *crc_func)(uint32_t seed, uint8_t* msg, uint32_t msglen);`
- Declares:
  - `extern crc_func calc_crc32c;`

## Dependencies

- Implemented by `crc32c.c` and `crc32c.S`.
- Included by `calcthread.c` for checksum job execution.

## Research Notes

- Consumers call through `calc_crc32c`, allowing runtime or initialization-time selection between software and hardware implementations.
- Hardware implementation is intentionally architecture-gated.
