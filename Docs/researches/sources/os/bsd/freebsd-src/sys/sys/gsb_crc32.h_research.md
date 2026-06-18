# File Research: sources/os/bsd/freebsd-src/sys/sys/gsb_crc32.h

## Purpose
Declares CRC32 and CRC32C calculation helpers, including kernel inline table CRC32 and architecture-specific CRC32C acceleration entry points.

## Main Interfaces
- Kernel-only external table: `crc32_tab`.
- Kernel inline functions:
  - `crc32_raw`
  - `crc32`
- Generic CRC32C: `calculate_crc32c`.
- Architecture-specific CRC32C:
  - `sse42_crc32c` for amd64/i386
  - `armv8_crc32c` for aarch64
- Testing helpers: `singletable_crc32c`, `multitable_crc32c`.

## Dependencies And Integration
Includes `sys/types.h`. Kernel `crc32` wraps `crc32_raw` with initial/final bitwise inversion. CRC32C implementations are selected elsewhere.

## Risk Notes
CRC32 and CRC32C are different polynomials; callers must use the right API. Architecture-specific prototypes must match CPU feature dispatch code.
