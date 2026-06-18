# sources/test-tools/stress-ng/core-arch.c

Purpose: maps compile-time architecture macros to a human-readable architecture string.

Important APIs and control flow: `stress_arch_get` is a preprocessor `#if/#elif` chain returning strings such as `ARM`, `RISC-V`, `x86-64`, or `unknown`.

State and persistence: stateless.

Dependencies and integration: depends on `core-arch.h` architecture detection macros and is used in build/runtime reporting.

Risks and test signals: string accuracy depends on macro detection order; new architectures need both header macro and string branch. Signal is expected buildinfo/runtime architecture output.
