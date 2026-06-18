# `sources/test-tools/fio/arch/arch-ia64.h`

Purpose: Provides IA-64 architecture primitives for fio.

Important APIs: Defines `FIO_ARCH arch_ia64`, pause hint `nop`, memory fence barriers, `ia64_popcnt()`, `arch_ffz()` using popcount arithmetic, `get_cpu_clock()` from `ar.itc`, and `arch_init()` setting `tsc_reliable = true`. Feature macros advertise init, ffz, and CPU clock support.

Control flow and integration: Included via `arch.h` for `__ia64__`. Generic timing and bit operations can use IA-64-specific implementations.

State and persistence: Mutates external `tsc_reliable` during init.

Dependencies: IA-64 inline assembly, `BITS_PER_LONG` configuration for bit operations, and compiler support for statement expressions.

Risks and test signals: IA-64 is uncommon, making bit operation and clock behavior easy to regress without cross-builds. Tests should compile for IA-64 and validate ffz semantics and monotonic clock handling where runtime is available.
