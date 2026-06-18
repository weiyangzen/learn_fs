<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_regs.c -->
# sources/test-tools/strace/src/linux/x86_64/arch_regs.c

Purpose: defines x86_64/i386 register storage and macros for generic ptrace register collection.
Important APIs/types/functions: `struct i386_user_regs_struct`, `x86_regs_union`, `x86_io`, `ARCH_REGS_FOR_GETREGSET`, `ARCH_IOVEC_FOR_GETREGSET`, `ARCH_PC_REG`, and `ARCH_SP_REG`.
Control flow: no functions; macros choose i386 or x86_64 PC/SP based on returned iovec length. State and persistence behavior: static register union updated by ptrace reads.
Dependencies and integration points: used by syscall entry/exit, argument extraction, error handling, and stack tracing.
Risks: i386 struct size is the ABI discriminator; overflow or wrong layout breaks mixed-personality tracing. Test signals: register-fetch tests for 64-bit and 32-bit tracees.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_regs.c -->
