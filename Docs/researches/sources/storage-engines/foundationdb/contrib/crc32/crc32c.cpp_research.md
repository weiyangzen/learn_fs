# sources/storage-engines/foundationdb/contrib/crc32/crc32c.cpp

## Purpose
Provides the public `crc32c_append()` implementation with runtime hardware acceleration where available and a table-driven software fallback.

## Important APIs, Types, And Functions
Public API is `extern "C" uint32_t crc32c_append(uint32_t crc, const uint8_t* input, size_t length)`. Important internal functions are `append_trivial()`, `append_adler_table()`, `append_table()`, `shift_crc()`, `append_hw()`, `ppc_hw()`, and `isHwCrcSupported()`. Hardware helpers map to Intel SSE4.2 CRC intrinsics, aarch64 inline assembly, or PowerPC wrapper code.

## Control Flow
At load time `hw_available` is initialized from CPUID or architecture macros. Calls to `crc32c_append()` dispatch to PowerPC wrapper, Intel/aarch64 hardware loop, or `append_table()`. Hardware loops align input, process large blocks as three independent CRC streams, combine them with shift tables, then handle trailing bytes. Table fallback aligns to word boundaries and folds 16-byte or 12-byte chunks through lookup tables.

## State And Persistence
Only static process state is `hw_available`. Lookup tables are static read-only data included from `crc32c-generated-constants.cpp`.

## Dependencies And Integration
Includes `crc32/crc32c.h`; includes CPU-specific headers `<cpuid.h>`, `<intrin.h>`, and `<nmmintrin.h>` conditionally. Integrated as the exported CRC32C function from the `crc32` static target.

## Risks
The code uses unaligned `reinterpret_cast` loads that are acceptable on x86 but architecture-sensitive. Aarch64 support assumes CRC instructions are present when `__aarch64__` is defined. PowerPC currently forces `isHwCrcSupported()` false, so `ppc_hw()` appears unreachable through normal dispatch. `hw_available` is computed at static initialization and cannot adapt to process migration or emulation quirks.

## Test Signals
Use known CRC32C vectors, randomized buffer splits to verify incremental appends, forced hardware/software dispatch comparisons, empty input, unaligned input, and large buffers crossing `LONG_SHIFT` and `SHORT_SHIFT` thresholds.
