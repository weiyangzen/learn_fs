# sources/test-tools/stress-ng/core-cpu.c

Purpose: x86 CPU identification, feature probing, DTLB sizing, and floating-point subnormal mode control.

Important APIs and control flow: `stress_cpu_is_x86` caches vendor/hypervisor CPUID detection; `STRESS_CPU_X86_HAS` generates per-feature cached CPUID helpers for clflush, waitpkg, rdseed, syscall, SSE, AVX/VNNI/AVX512, movdiri, serialize, and others; DTLB helpers decode CPUID descriptors/subleaves and may iterate CPUs by setting affinity; FP helpers toggle SSE DAZ/FTZ bits in MXCSR.

State and persistence: many function-local static caches store CPUID results; DTLB probing can temporarily mutate process affinity; FP helpers mutate current thread floating-point control state.

Dependencies and integration: depends on `core-arch.h`, `core-asm-x86.h`, `core-builtin.h`, scheduler affinity, and compiler intrinsics.

Risks and test signals: CPUID leaf assumptions vary on virtual/old CPUs; DTLB helper restores affinity to CPU 0 rather than the original mask; subnormal toggles affect IEEE behavior. Signals are feature-gated stressors using safe instruction paths and CPU feature reporting correctness.
