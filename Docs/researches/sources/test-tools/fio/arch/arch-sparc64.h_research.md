# `sources/test-tools/fio/arch/arch-sparc64.h`

Purpose: Provides SPARC64 architecture id and memory barriers for fio.

Important APIs: Defines `FIO_ARCH arch_sparc64`, empty `nop`, `membar_safe(type)` using a branch-around sequence with `membar`, `read_barrier()` as `#LoadLoad`, and `write_barrier()` as `#StoreStore`.

Control flow and integration: Intended for inclusion by `arch.h` on SPARC64. Generic paths cover optional clock/syscall/ffz features.

State and persistence: No state.

Dependencies: SPARC64 inline assembly and memory barrier syntax.

Risks and test signals: In `arch.h`, the `__sparc__` check precedes `__sparc64__`, so compilers defining both may select the 32-bit SPARC header instead. Tests should verify preprocessing on real SPARC64 toolchains.
