<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/get_error.c -->
# sources/test-tools/strace/src/linux/x86_64/get_error.c

Purpose: converts architecture return registers into strace success or errno state on x86.
Important APIs/types/functions: `arch_get_error`, `is_negated_errno`, `x86_io`, `i386_regs.eax`, `x86_64_regs.rax`, `tcp->u_rval`, and `tcp->u_error`.
Control flow: sign-extends i386 `eax`, keeps x86_64/x32 64-bit `rax`, then treats negated errno values as errors when requested.
State and persistence behavior: writes only per-syscall `tcb` return fields. Dependencies and integration points: syscall exit path and `negated_errno.h`.
Risks: x32 needs 64-bit returns for calls such as llseek; truncation would be visible. Test signals: success/error return tests for i386, x86_64, and x32.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/get_error.c -->
