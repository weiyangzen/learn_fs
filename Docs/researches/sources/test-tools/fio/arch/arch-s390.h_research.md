# `sources/test-tools/fio/arch/arch-s390.h`

Purpose: Provides s390/s390x fio architecture primitives and CPU clock support.

Important APIs: Defines `FIO_ARCH arch_s390`, `nop`, barriers using `bcr 15,0`, `get_cpu_clock()` using `stckf` when `CONFIG_S390_Z196_FACILITIES` is set or `stck` otherwise, shifts the clock by 12, sets `ARCH_CPU_CLOCK_CYCLES_PER_USEC 1`, enables CPU clock/init, undefines `ARCH_CPU_CLOCK_WRAPS`, and sets `tsc_reliable = true` in init.

Control flow and integration: Selected by `arch.h` for `__s390x__` or `__s390__`. Timing code can use the architecture clock without wrap assumptions.

State and persistence: Mutates external `tsc_reliable` during init.

Dependencies: s390 inline assembly and optional facility configuration.

Risks and test signals: Clock scaling assumptions are architecture-specific. Tests should build/run on s390x, validate monotonic timing, and exercise rate limiting and latency accounting.
