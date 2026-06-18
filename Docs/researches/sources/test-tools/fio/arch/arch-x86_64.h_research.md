# `sources/test-tools/fio/arch/arch-x86_64.h`

Purpose: Provides x86_64 fio architecture primitives, CPU clock, random instructions, bit operations, and Linux syscall wrappers.

Important APIs: Defines `do_cpuid()`, includes `arch-x86-common.h`, sets `FIO_ARCH arch_x86_64`, huge page size 2 MiB, `rep;nop`, compiler barriers, `arch_ffz()` using `bsf`, `tsc_barrier()` using `mfence`, `get_cpu_clock()` using `rdtsc`, RDRAND/RDSEED opcodes, `arch_rand_long()`, `arch_rand_seed()`, and `__do_syscall0` through `__do_syscall6` using the x86_64 Linux syscall ABI. Enables ffz, SSE4.2, CPU clock, and direct syscall support.

Control flow and integration: Selected by `arch.h` for `__x86_64__`. Generic random, syscall, and timing code can use these fast paths.

State and persistence: No direct state; common x86 init sets `tsc_reliable` and `arch_random`.

Dependencies: x86_64 inline assembly, Linux syscall calling convention, and CPUID feature detection.

Risks and test signals: `arch_rand_seed()` returns 0 regardless of carry flag, so callers cannot detect RDSEED failure from the return value. `arch_rand_long()` returns the retry counter register rather than a normalized boolean, so semantics need caller review. Direct syscall wrappers bypass libc and must match kernel ABI. Tests should cover direct io_uring syscalls, random seeding fallback, and TSC timing on varied CPUs.
