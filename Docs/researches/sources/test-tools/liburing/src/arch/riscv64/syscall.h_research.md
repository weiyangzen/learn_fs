# sources/test-tools/liburing/src/arch/riscv64/syscall.h

## sources/test-tools/liburing/src/arch/riscv64/syscall.h

Purpose: RISC-V 64 raw syscall macro layer for liburing nolibc operation.

Important APIs/macros: `__do_syscall0` through `__do_syscall6`; syscall number in `a7`, arguments in `a0`-`a5`, `ecall` instruction; includes `../syscall-defs.h` for typed wrappers.

Control flow: native raw asm selected when `__riscv && __riscv_xlen == 64`, otherwise generic libc syscall wrappers are used.

State and persistence: none.

Dependencies/integration: Linux RISC-V syscall ABI and compiler register variable support.

Risks: clobber lists differ for one-argument vs multi-argument macros to account for return registers; mistakes would corrupt syscall arguments/results. Raw negative errors must be handled by callers.

Test signals: riscv64 CI compilation and nolibc runtime where available.
