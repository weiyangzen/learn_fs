# File Research: sources/windows/reactos/drivers/filesystems/btrfs/blake2-impl.h

Bundled BLAKE2 reference implementation support header used by `blake2b-ref.c`.

Key contents:
- Defines `BLAKE2_INLINE` portably for C89/MSVC/GCC/C99/C++ contexts.
- Forces `NATIVE_LITTLE_ENDIAN`, causing `load16()`, `load32()`, `load64()`, `store16()`, `store32()`, and `store64()` to use `memcpy()` rather than byte assembly on this build.
- Provides endian-independent 48-bit load/store helpers and 32/64-bit rotate-right helpers.
- Defines `BLAKE2_PACKED()` for MSVC and GCC-style compilers.
- Defines BLAKE2b public constants for block, output, key, salt, and personalization sizes.
- Declares the internal `blake2b_state` and packed `blake2b_param` structures used by the reference compressor.

Important invariants:
- The header assumes the target is little-endian. That matches Windows/ReactOS x86/x64 expectations but is not a portable runtime check.
- Multi-byte load/store helpers use `memcpy()` for unaligned access safety when native little-endian is enabled.
- The packed parameter block layout is part of the BLAKE2b initialization contract; field offsets must remain exact.

Filesystem relevance:
- Btrfs can use BLAKE2b as a checksum algorithm. This header supplies the low-level primitives and state layout for computing those checksums inside the kernel driver.

Notable risks:
- `NATIVE_LITTLE_ENDIAN` is unconditionally defined, so a big-endian build would produce incorrect results unless changed.
- This is vendored cryptographic/hash reference code; local divergence from upstream should be treated cautiously.
