# `sources/test-tools/fio/arch/arch-x86.h`

Purpose: Provides 32-bit x86 fio architecture primitives.

Important APIs: Defines `do_cpuid()` using `xchgl %%ebx` for PIC-safe EBX handling, includes `arch-x86-common.h`, defines `FIO_ARCH arch_x86`, huge page size 4 MiB, `rep;nop`, compiler barriers, `arch_ffz()` using `bsfl`, and `get_cpu_clock()` using `rdtsc` with `=A`. Enables ffz and CPU clock features.

Control flow and integration: Selected by `arch.h` for `__i386__`. Shared x86 init handles vendor and TSC/RDRAND feature discovery.

State and persistence: No state directly; common init mutates x86 globals.

Dependencies: 32-bit x86 inline assembly and compiler support for `=A`.

Risks and test signals: `rdtsc` reliability depends on `tsc_reliable` detection elsewhere. Tests should build i686 targets and run timing/rate tests under both bare metal and virtualized environments.
