# sources/test-tools/stress-ng/core-target-clones.h

## Purpose
`core-target-clones.h` centralizes compiler `target_clones` attribute selection for CPU-dispatched optimized functions.

## Important APIs, Types, And Functions
The public output is the `TARGET_CLONES` macro. On supported x86 builds it can expand to `__attribute__((target_clones(...)))` with MMX, SSE, AVX, Intel microarchitecture, and AMD `znver` targets plus `default`. On supported PPC64 builds it can include Power9, Power10, and Power11 targets. ICC and small builds disable target clones.

## Control Flow
There is no runtime logic in this header, but compiled functions annotated with `TARGET_CLONES` gain compiler-generated runtime dispatch. The preprocessor builds `TARGET_CLONES_ALL` only when architecture, compiler, and individual target probes are present; otherwise `TARGET_CLONES` becomes empty.

## State And Persistence
No source-level mutable state exists. The compiled binary may contain multiple function versions and dispatch thunks, which affects code size and runtime CPU feature selection.

## Dependencies And Integration Points
It includes `core-arch.h` and uses many build-time feature macros. `core-workload.c` uses `TARGET_CLONES` on math, memory-read, and vector workload helpers; other performance-sensitive stressors may include it.

## Risks
Target strings are compiler-version sensitive. Enabling an unsupported target can fail compilation or produce illegal instructions if compiler dispatch is incorrect. Disabling target clones for small builds and ICC prevents known compatibility and binary-size issues.

## Test Signals
Builds across x86, PPC64, GCC, Clang, musl, ICC, and `HAVE_BUILD_SMALL` configurations validate this header. Runtime workload and vector stressors exercise the generated dispatch paths.
