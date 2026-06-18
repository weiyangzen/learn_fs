<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/citycrc.h -->
# sources/user-network-fs/nfs-ganesha/src/include/citycrc.h

## Purpose
`citycrc.h` declares CityHash variants that use CRC instructions, including 128-bit and 256-bit hash outputs.

## Important APIs, types, and functions
- `CityHashCrc128()` computes a 128-bit CRC-accelerated CityHash.
- `CityHashCrc128WithSeed()` computes a seeded 128-bit CRC CityHash.
- `CityHashCrc256()` writes four 64-bit words to a caller-provided result array.

## Control flow
Callers pass a byte buffer and length, plus optional seed or output array. Implementations use CRC-capable CPU instructions such as `_mm_crc32_u64()` where available.

## State and persistence
The header has no state. Output buffers are caller-owned.

## Dependencies and integration points
It includes `city.h` for `uint128` and `uint64` types. It integrates with code that wants faster or wider non-cryptographic hashes on CRC-capable platforms.

## Risks
- CRC variants require CPU/compiler support for the needed intrinsics in implementation code.
- These hashes are still non-cryptographic and must not be used as security primitives.
- Runtime dispatch or build flags must prevent illegal-instruction failures on unsupported CPUs.
- `CityHashCrc256()` requires the caller to provide space for four `uint64` values.

## Test signals
- Build tests should cover CRC-enabled and CRC-disabled targets.
- Runtime tests should verify CPU feature gating before calling CRC implementations.
- Known-vector tests should cover seeded and unseeded outputs and the 256-bit four-word result.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/citycrc.h -->
