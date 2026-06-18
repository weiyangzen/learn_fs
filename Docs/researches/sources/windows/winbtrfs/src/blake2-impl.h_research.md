# File Research: sources/windows/winbtrfs/src/blake2-impl.h

## Purpose

`blake2-impl.h` is the local BLAKE2 support header used by WinBtrfs’s reference BLAKE2b implementation. It provides endian-safe load/store helpers, rotate helpers, packing macros, constants, and the `blake2b_state` / `blake2b_param` structures.

## Main Contents

- Defines `BLAKE2_INLINE` depending on C/C++ mode and compiler.
- Forces `NATIVE_LITTLE_ENDIAN`, which matches supported Windows targets.
- Provides inline little-endian helpers:
  - `load16`, `load32`, `load48`, `load64`
  - `store16`, `store32`, `store48`, `store64`
- Provides rotate helpers:
  - `rotr32`
  - `rotr64`
- Defines `BLAKE2_PACKED` for MSVC and GCC-style compilers.
- Defines BLAKE2b constants:
  - block size: 128 bytes
  - output size: 64 bytes
  - key size: 64 bytes
  - salt/personalization size: 16 bytes each
- Defines `blake2b_state`:
  - chaining words `h[8]`
  - byte counter `t[2]`
  - finalization flags `f[2]`
  - 128-byte buffer
  - buffer length, output length, last-node flag
- Defines packed `blake2b_param`:
  - digest/key/fanout/depth fields
  - leaf/node/xof fields
  - reserved area
  - salt and personalization arrays

## Implementation Notes

- On native little-endian builds, load/store uses `memcpy`, avoiding unaligned access and strict-aliasing problems.
- Non-little-endian fallback code exists for 16/32/64-bit helpers, but the header unconditionally defines `NATIVE_LITTLE_ENDIAN`.
- `load48` and `store48` are byte-wise helpers independent of native-endian mode.
- The file contains only static inline helpers and type definitions; it exports no standalone function.

## Integration

`blake2b-ref.c` includes this header for BLAKE2b compression, initialization, update, and finalization. WinBtrfs uses BLAKE2b as one of the supported Btrfs checksum algorithms elsewhere in the driver.
