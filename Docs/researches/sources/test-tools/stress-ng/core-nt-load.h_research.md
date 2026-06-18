# sources/test-tools/stress-ng/core-nt-load.h

Purpose: conditionally exposes non-temporal load intrinsics for cache-bypassing memory access stressors.

Important APIs/types: inline `stress_nt_load128`, `stress_nt_load64`, `stress_nt_load32`, and `stress_nt_load_double`, each paired with a `HAVE_NT_LOAD*` macro when available.

Control flow: compile-time feature checks gate each inline implementation. Available implementations use `__builtin_nontemporal_load`.

State/persistence: no state; helpers read caller-provided addresses.

Dependencies/integration: compiler feature macros, fixed-width integer types, `__uint128_t`, and `ALWAYS_INLINE`.

Risks: no fallback functions are provided; callers must guard use with `HAVE_NT_LOAD*`. Alignment and hardware semantics are caller/compiler responsibilities.

Test signals: Clang/GCC feature matrix builds, macro-guarded users, and memory stressors on architectures without support.
