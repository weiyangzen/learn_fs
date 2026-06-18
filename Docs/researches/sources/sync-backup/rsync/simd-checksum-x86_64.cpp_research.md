<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/simd-checksum-x86_64.cpp -->
# sources/sync-backup/rsync/simd-checksum-x86_64.cpp

Purpose: x86-64 C++ implementation of rsync's weak rolling checksum fast path. It replaces the scalar `get_checksum1()` loop with multiversioned SSE2, SSSE3, and AVX2 routines when `USE_ROLL_SIMD` is enabled, while keeping a scalar tail path for small or leftover byte ranges.

Important APIs/types/functions: the exported C symbol is `uint32 get_checksum1(char *buf1, int32 len)`. Internal workers are `get_checksum1_avx2_64()`, optional external `get_checksum1_avx2_asm()`, `get_checksum1_ssse3_32()`, `get_checksum1_sse2_32()`, `get_checksum1_default_1()`, and `get_checksum1_cpp()`. The file defines unaligned vector typedefs `__m128i_u` and `__m256i_u`, SSE2 compatibility macros that emulate SSSE3-style byte multiply/add operations, `roll_asm_have_avx2()` for runtime gating of the assembly AVX2 path, plus optional benchmark and self-test `main()` functions behind `BENCHMARK_SIMD_CHECKSUM1` and `TEST_SIMD_CHECKSUM1`.

Control flow: `get_checksum1_cpp()` initializes `s1`, `s2`, and index `i`, then attempts increasingly smaller vector blocks. AVX2 consumes 64-byte chunks if available, SSSE3 consumes 32-byte chunks if runtime multiversioning selects it, SSE2 consumes remaining 32-byte chunks, and `get_checksum1_default_1()` finishes 4-byte groups and final bytes. Each vector loop computes the same recurrence as the classic rsync rolling checksum: accumulate `s1` as byte sums plus `CHAR_OFFSET`, and `s2` as the weighted prefix-sum accumulator. The final return packs `(s1 & 0xffff) + (s2 << 16)`.

State and persistence behavior: the routines are pure over the input buffer and checksum accumulators. The only persistent process state is the cached `roll_asm_have_avx2()` result when assembly is enabled. There is no filesystem or network state.

Dependencies and integration points: this file depends on `rsync.h`, rsync integer aliases, `CHAR_OFFSET`, GCC/clang target attributes, and `<immintrin.h>`. It is compiled only for `__x86_64__` as C++ and only emits the optimized symbol when `USE_ROLL_SIMD` is configured. The exported `get_checksum1()` integrates with rsync's block matching and rolling checksum pipeline.

Risks: correctness depends on exact signed-byte handling, block-boundary math, and consistent `CHAR_OFFSET` constants between scalar and vector paths. Runtime CPU dispatch is subtle: the assembly AVX2 path must be gated or it can SIGILL on non-AVX2 CPUs, and compiler multiversioning behavior differs between GCC and clang. The AVX2 `CHAR_OFFSET` branch uses 32-byte constants in comments/code even though the loop consumes 64 bytes, so any nonzero `CHAR_OFFSET` build deserves focused validation. Alignment handling and final tail rollover are high-value regression targets.

Test signals: the `TEST_SIMD_CHECKSUM1` harness compares scalar, SSE2, SSSE3, AVX2, and auto dispatch across aligned and unaligned buffers and sizes from 1 through 65536. `BENCHMARK_SIMD_CHECKSUM1` provides throughput comparisons. Build coverage must include both intrinsic and optional `USE_ROLL_ASM` variants.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/simd-checksum-x86_64.cpp -->
