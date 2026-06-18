# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/SYS.h

This header defines RISC-V libc syscall wrapper macros. `SYSTRAP` loads the syscall number into `t6` and executes `ecall`; normal wrappers then tail-call `__cerror` on the error path and `ret` on success.

`SYSTRAP_NOERROR` pads with `nop`s to match the size of the normal error jump sequence, preserving layout expectations. The header supplies `RSYSCALL`, `WSYSCALL`, `PSEUDO`, and no-error variants used by the RISC-V syscall files.
