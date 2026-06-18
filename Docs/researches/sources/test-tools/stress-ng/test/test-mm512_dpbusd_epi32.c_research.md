<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm512_dpbusd_epi32.c -->
# sources/test-tools/stress-ng/test/test-mm512_dpbusd_epi32.c

Purpose: compile and runtime smoke probe for the x86 SIMD intrinsic `_mm512_dpbusd_epi32` using 512-bit integer vectors; it verifies that the compiler accepts the header, target attribute, vector type, and intrinsic call used by stress-ng feature detection.

Important APIs/types/functions: includes `immintrin.h`, `string.h`, `stdint.h`; uses types `__m512i`; defines `rndset`, `__attribute__`; uses intrinsics `_mm512_dpbusd_epi32`; calls `target`, `_mm512_dpbusd_epi32`.

Control flow: helper definitions `rndset`, `__attribute__` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value SIMD probes fill vector storage with `rndset()`, execute the intrinsic, and return an integer lane from the result or source vector.

State and persistence behavior: all state is stack-local vector or byte-buffer data seeded by `rndset()` from the helper function address. No files, kernel objects, or persistent settings are intentionally created; executing the binary may require CPU support for the targeted instruction set.

Dependencies and integration points: depends on headers `immintrin.h`, `string.h`, `stdint.h`; compiler target attributes `avx512vnni`; x86 intrinsic support from `immintrin.h` and matching compiler code generation. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SIMD probes can compile but fail with illegal-instruction behavior if run on a CPU lacking the requested ISA despite the compiler accepting the target attribute. the integer return reads bytes from vector storage solely as an anti-optimization signal, so it is not a semantic correctness check. Test signals are successful compilation; successful linking; accepted intrinsic code generation for `_mm512_dpbusd_epi32`; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm512_dpbusd_epi32.c -->
