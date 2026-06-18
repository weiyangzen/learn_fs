# `sources/test-tools/fio/arch/arch-sparc.h`

Purpose: Minimal 32-bit SPARC architecture support for fio.

Important APIs: Defines `FIO_ARCH arch_sparc`, empty `nop`, and compiler memory barriers for read/write barriers.

Control flow and integration: Selected by `arch.h` for `__sparc__` before the `__sparc64__` branch. Generic optional features are used.

State and persistence: No state.

Dependencies: Compiler support for inline assembly memory clobbers.

Risks and test signals: Ordering primitives are compiler-only, unlike SPARC64’s membar use. Branch ordering in `arch.h` should be checked because some SPARC64 compilers may also define `__sparc__`. Tests should compile for SPARC and SPARC64 and verify the intended header is selected.
