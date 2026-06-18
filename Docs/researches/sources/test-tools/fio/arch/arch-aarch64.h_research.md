# `sources/test-tools/fio/arch/arch-aarch64.h`

Purpose: Provides fio’s AArch64 architecture contract: architecture id, pause/barrier primitives, find-first-zero, CPU clock, init hook, and direct syscall macros.

Important APIs: Defines `FIO_ARCH arch_aarch64`, `nop` as `yield`, full barriers with `__sync_synchronize()`, `arch_ffz()` using `rbit`/`clz`, `get_cpu_clock()` from `cntvct_el0` after `isb`, `arch_init()` setting `tsc_reliable = true`, and `__do_syscall0` through `__do_syscall6` using `svc 0` and registers `x8`, `x0`-`x5`.

Control flow and integration: Included via `arch.h` when `__aarch64__` is defined. Feature macros `ARCH_HAVE_FFZ`, `ARCH_HAVE_CPU_CLOCK`, `ARCH_HAVE_INIT`, and `FIO_ARCH_HAS_SYSCALL` enable generic code paths.

State and persistence: No persistent state beyond setting external `tsc_reliable` during arch initialization.

Dependencies: Uses inline assembly, Linux/AArch64 syscall ABI expectations, and common fio architecture enums.

Risks and test signals: Direct syscall macros are ABI-sensitive and assume Linux register conventions. CPU clock availability depends on user access to `cntvct_el0`. Tests should build/run fio on AArch64, exercise io_uring direct syscall paths, random timing code, and ffz users.
