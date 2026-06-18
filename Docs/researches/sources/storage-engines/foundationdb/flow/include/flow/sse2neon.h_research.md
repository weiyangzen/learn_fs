# sources/storage-engines/foundationdb/flow/include/flow/sse2neon.h

## Purpose
This vendored header is a translation layer from Intel SSE/SSE2/SSSE3/SSE4/AES-style intrinsics to Arm NEON intrinsics. It lets code written against `_mm_*`, `__m128`, and `__m128i` compile on Arm/AArch64 without rewriting call sites.

## Important APIs, Types, and Functions
The header defines `_MM_SHUFFLE`, `__constrange`, `__m64`, `__m128`, `__m128i`, `SIMDVec`, many `vreinterpretq_*` compatibility macros, and hundreds of `_mm_*` functions/macros. Covered families include prefetch, set/get, load/store, logic, shuffle/permute, shifts, masks, arithmetic, saturated arithmetic, horizontal operations, comparisons, conversions, packing/unpacking, extraction/insertion, carry-less multiply, AES round support, streaming fences, cache flush stubs, and aligned allocation (`_mm_malloc`, `_mm_free`).

## Control Flow
Most intrinsics are `FORCE_INLINE` wrappers that reinterpret x86 vector types as NEON lane types, call one or more NEON intrinsics, then reinterpret the result back. Immediate-sensitive operations such as `_mm_shuffle_ps`, `_mm_shuffle_epi32`, shifts, alignment, extract, and insert are macros because compilers require literal lane/immediate values. Several implementations branch on `__clang__`, `__aarch64__`, `__GNUC__`, and `__ARM_FEATURE_CRYPTO` to choose compiler builtins, AArch64 lane operations, inline assembly, or fallback sequences. Crypto support chooses hardware polynomial/AES intrinsics when available and software NEON polyfills otherwise.

## State and Persistence Behavior
The header has no durable state. Runtime-visible state is limited to stack temporaries and static lookup tables in AES fallback code. It does affect ABI and code generation by defining x86 intrinsic type names as NEON vector types and by pushing/popping `FORCE_INLINE` and `ALIGN_STRUCT` macros around its contents.

## Dependencies and Integration Points
It depends on `<arm_neon.h>`, compiler vector extensions, `stdint.h`, `stdlib.h`, and POSIX `posix_memalign` for aligned allocation. It is an external project imported into the Flow include tree; FoundationDB Arm builds can include it in code paths that otherwise use Intel intrinsics.

## Risks
Semantic mismatches are the central risk. Floating-point rounding, reciprocal/square-root approximations, NaN comparisons, saturated arithmetic, immediate handling, endian assumptions, alignment behavior, and cache/fence semantics may differ from real SSE. Some comments call out approximation or limitations, such as Armv7 round-to-even limitations and `_mm_clflush` being a no-op. Macro implementations can evaluate arguments in expression contexts and depend on GNU statement expressions. Crypto fallbacks are performance- and correctness-sensitive. Because this file is vendored, local changes can diverge from upstream `sse2neon` behavior.

## Test Signals
Best tests compare outputs against native SSE on x86 for representative vectors, including edge cases for NaN, signed overflow, saturation, rounding, masks, shuffle immediates, AES/carry-less multiply, and unaligned loads. Build coverage should include Clang/GCC, Armv7 if supported, AArch64, with and without crypto extensions. Performance tests are appropriate for hot vector code that depends on approximate reciprocal/sqrt or crypto paths.
