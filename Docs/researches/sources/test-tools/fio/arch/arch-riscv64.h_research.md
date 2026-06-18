# `sources/test-tools/fio/arch/arch-riscv64.h`

Purpose: Provides RISC-V 64-bit fio architecture primitives and Linux direct syscall wrappers.

Important APIs: Defines `FIO_ARCH arch_riscv64`, `nop`, read/write fences, `get_cpu_clock()` using `rdtime`, `arch_init()` setting `tsc_reliable = true`, and `__do_syscall0` through `__do_syscall6` using `ecall` with `a7` syscall number and `a0`-`a5` arguments. `ARCH_HAVE_CPU_CLOCK`, `ARCH_HAVE_INIT`, and `FIO_ARCH_HAS_SYSCALL` are enabled.

Control flow and integration: Selected by `arch.h` for `__riscv` with `__riscv_xlen == 64`. Used by timing and syscall helper code.

State and persistence: Mutates external `tsc_reliable` during init.

Dependencies: RISC-V inline assembly and Linux syscall ABI. `rdtime` user availability depends on platform/kernel configuration.

Risks and test signals: Clobber lists differ between syscall macros (`__do_syscallM` clobbers `a1`); ABI correctness is critical. Tests should cross-build and run io_uring/syscall paths plus timing workloads on RISC-V 64.
