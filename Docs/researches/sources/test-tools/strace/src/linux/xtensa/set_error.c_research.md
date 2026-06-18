<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/set_error.c -->
# sources/test-tools/strace/src/linux/xtensa/set_error.c

Purpose: writes synthetic syscall return values into Xtensa registers.
Important APIs/types/functions: `arch_set_error`, `arch_set_success`, `xtensa_regs.a[windowbase * 4 + 2]`, and `set_regs`.
Control flow: stores negative errno or success value into the current window's return register and writes the register set back to the tracee. State and persistence behavior: mutates tracee registers.
Dependencies and integration points: syscall fault injection and tampering. Risks: windowbase miscalculation changes the wrong register. Test signals: Xtensa fault-injection success/error rewrite tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/set_error.c -->
