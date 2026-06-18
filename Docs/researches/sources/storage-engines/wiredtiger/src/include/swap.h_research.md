# sources/storage-engines/wiredtiger/src/include/swap.h

Purpose: `swap.h` centralizes byte-swap helpers for 16-, 32-, and 64-bit unsigned values so on-disk little/big-endian conversions and metadata encodings can use one internal spelling.

Important APIs: `__wt_bswap16`, `__wt_bswap32`, and `__wt_bswap64` are defined as compiler or platform intrinsics on MSVC, Clang, GCC, and Solaris where available, with inline bit-manipulation fallbacks otherwise.

Control flow and state: preprocessor feature detection chooses the implementation at compile time. The fallback functions are pure arithmetic transformations, have no side effects, and preserve no state.

Dependencies and integration points: the header includes `misc.h` and uses WiredTiger's `WT_INLINE` convention. It is a low-level dependency for packed disk structures, compressor/encryptor prefixes, block metadata, checksum paths, and any code that must normalize endian-specific byte order.

Risks: feature-detection branches must match compiler versions correctly. The fallback constants rely on unsigned widths and should stay warning-clean across 32/64-bit platforms. Misuse on already-swapped values is outside the helper's control and can corrupt persistent formats.

Test signals: build coverage across GCC, Clang, MSVC, and Solaris-like branches; value tests for fixed byte patterns such as `0x0102`, `0x01020304`, and `0x0102030405060708`; and endian-sensitive recovery/format tests that read files produced on the opposite endian mode when such coverage is available.
