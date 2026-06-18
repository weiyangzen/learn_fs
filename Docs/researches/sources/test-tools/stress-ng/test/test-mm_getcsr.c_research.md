<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_getcsr.c -->
# sources/test-tools/stress-ng/test/test-mm_getcsr.c

Purpose: compile and runtime smoke probe for the x86 SIMD intrinsic `_mm_getcsr` using 128-bit integer vectors; it verifies that the compiler accepts the header, target attribute, vector type, and intrinsic call used by stress-ng feature detection.

Important APIs/types/functions: includes `immintrin.h`; defines `main`; uses intrinsics `_mm_getcsr`; calls `_mm_getcsr`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value SIMD probes fill vector storage with `rndset()`, execute the intrinsic, and return an integer lane from the result or source vector.

State and persistence behavior: all state is stack-local vector or byte-buffer data seeded by `rndset()` from the helper function address. No files, kernel objects, or persistent settings are intentionally created; executing the binary may require CPU support for the targeted instruction set.

Dependencies and integration points: depends on headers `immintrin.h`; x86 intrinsic support from `immintrin.h` and matching compiler code generation. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SIMD probes can compile but fail with illegal-instruction behavior if run on a CPU lacking the requested ISA despite the compiler accepting the target attribute. Test signals are successful compilation; successful linking; accepted intrinsic code generation for `_mm_getcsr`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_getcsr.c -->
