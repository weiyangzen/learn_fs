# sources/storage-engines/wiredtiger/src/checksum/x86/crc32-x86-alt.c

## Purpose
This file preserves compatibility with a historical Windows x86-64 hardware CRC implementation that could produce different values for buffers that were not 8-byte aligned or whose length was not a multiple of 8. It is not used to write new checksums; it is a secondary read-side match path for legacy data.

## Important APIs, Types, and Functions
`__checksum_alt(const void *chunk, size_t len)` is a private alternate CRC32C calculation using `_mm_crc32_u8` and `_mm_crc32_u64`. `__wt_checksum_alt_match(const void *chunk, size_t len, uint32_t v)` is the exported compatibility predicate declared in `extern.h` when built for `_M_AMD64` without `HAVE_NO_CRC32_HARDWARE`.

## Control Flow
The alternate function starts from `0xffffffff`, consumes bytes until a 4-byte boundary, processes 8-byte words with SSE4.2 CRC instructions, then consumes trailing bytes. The exported matcher runs CPUID leaf 1, checks the SSE4.2 ECX bit, and only computes the alternate checksum when the CPU supports the instruction set.

## State and Persistence
No state is stored. Persistence behavior is compatibility-oriented: old disk/log data may contain checksums from the historic calculation, and `__wt_checksum_match` can accept either the current checksum or this alternate value on affected Windows builds.

## Dependencies and Integration Points
The file depends on `wiredtiger_config.h`, MSVC intrinsic availability, and CPUID. It integrates with `misc_inline.h`, where `__wt_checksum_match` includes `__wt_checksum_alt_match` in the appropriate build configuration. It complements `crc32-x86.c`, which provides the current x86 checksum writer.

## Risks and Edge Cases
This path must never become the preferred write path or it could perpetuate legacy checksum divergence. Its availability is build- and platform-specific, so tests that only run on non-Windows platforms will not exercise it. The same alignment and tail-length cases that caused the compatibility concern should remain covered.

## Test Signals
Useful signals are checksum compatibility tests on Windows x86-64 with SSE4.2, block/log recovery fixtures containing legacy checksums, and generic checksum tests that verify normal checksum matching is not weakened on platforms where the alternate function is absent.
