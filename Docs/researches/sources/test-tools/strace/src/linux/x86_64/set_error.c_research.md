<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/set_error.c -->
# sources/test-tools/strace/src/linux/x86_64/set_error.c

Purpose: writes synthetic error or success return values back into x86 tracee registers.
Important APIs/types/functions: `arch_set_error`, `arch_set_success`, `tcp->u_error`, `tcp->u_rval`, `i386_regs.eax`, `x86_64_regs.rax`, `upoke`, and `RAX` register offset.
Control flow: chooses i386 or 64-bit return register by current personality, stores local mirror, then pokes the kernel register slot.
State and persistence behavior: mutates tracee register state for injection/tampering. Dependencies and integration points: fault injection and syscall return modification.
Risks: wrong personality or register offset changes the wrong register. Test signals: syscall fault injection tests on i386 and x86_64 personalities.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/set_error.c -->
