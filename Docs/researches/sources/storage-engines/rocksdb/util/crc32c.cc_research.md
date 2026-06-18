# sources/storage-engines/rocksdb/util/crc32c.cc

Purpose: implements RocksDB's CRC-32C engine behind `util/crc32c.h`, including a portable table-driven fallback, platform-specific fast dispatch, x86 SSE4.2/PCLMUL three-way acceleration, Power8 and Arm64 integration, support probing text, and logarithmic CRC concatenation through `Crc32cCombine`.

Important APIs and functions: `Extend()` is the exported entry point and delegates to static `ChosenExtend`, initialized by `Choose_Extend()`. `ExtendImpl<CRC32>()` is the common byte/alignment loop, using `DefaultCRC32()` for either table or SSE instruction chunks. `ExtendPPCImpl()` and `ExtendARMImpl()` wrap platform implementations. `IsFastCrc32Supported()` reports the compiled/runtime-selected fast path. The x86-only `crc32c_3way()` parallelizes long inputs through three CRC lanes and `_mm_clmulepi64_si128()`. `Crc32cCombine()` converts RocksDB's inverted CRC values to pure CRC space, advances the first CRC over virtual zeroes, cancels the second initializer, and combines with the second CRC.

Control flow: the file starts with lookup tables and low-level chunk helpers, then platform probes, then dispatch. `ExtendImpl()` aligns the pointer, consumes 16-byte and 8-byte chunks, and finishes bytewise. On x86 with SSE4.2 and PCLMUL, `Choose_Extend()` prefers `crc32c_3way()` unless disabled. On Arm/PPC it requires runtime feature checks before using hardware paths. Combine logic uses constexpr GF(2) multiplication tables and `CountTrailingZeroBits()` to advance by powers of zero blocks.

State and persistence: `ChosenExtend` is a process-static function pointer selected at load time. On Arm, global `pmull_runtime_flag` records PMULL availability. On PPC, `arch_ppc_crc32` caches probe result. CRC values are deterministic file-format/state values, so table constants, inversion semantics, masking compatibility, and combine math are persistence-critical.

Dependencies and integration: depends on `util/coding.h`, `util/math.h`, `util/crc32c_arm64.h`, and, on PPC, `crc32c_ppc.*` plus constants. Callers include file checksums, block/data verification, WAL/SST checksum paths, and tests. The code is heavily gated by compiler macros and CPU feature macros.

Risks: static dispatch on x86 assumes binaries are only run where compiled CPU features are valid; runtime detection is explicitly removed there. Unaligned casts are intentionally used in fast paths and need sanitizer suppression. Any change to polynomial constants, inversion, endian handling, or mask semantics breaks stored checksums. Static initialization depends on runtime probe functions being safe during load.

Test signals: `crc32c_test.cc` covers RFC vectors, small/unaligned/large inputs, incremental `Extend()`, masking round trips, and `Crc32cCombine()` over many sizes including a large second input.
