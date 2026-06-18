# `sources/test-tools/fio/arch/arch-mips.h`

Purpose: Minimal MIPS/MIPS64 architecture support for fio.

Important APIs: Defines `FIO_ARCH arch_mips`, sets `__SANE_USERSPACE_TYPES__` if absent to influence Linux type headers, and defines read/write barriers plus `nop` as compiler memory barriers.

Control flow and integration: Included by `arch.h` for `__mips__` or `__mips64__`. Generic code handles missing optional features.

State and persistence: No state.

Dependencies: Compiler memory clobber support and Linux userspace type header behavior.

Risks and test signals: The include guard name says `ARCH_MIPS64_H` while covering both MIPS and MIPS64; harmless but potentially confusing. Hardware barrier strength is minimal. Tests should cross-compile for 32- and 64-bit MIPS and run basic fio jobs if hardware/emulation is available.
