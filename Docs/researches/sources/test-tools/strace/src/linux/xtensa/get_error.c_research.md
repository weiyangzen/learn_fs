<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/get_error.c -->
# sources/test-tools/strace/src/linux/xtensa/get_error.c

Purpose: converts Xtensa return register state into strace return/error fields.
Important APIs/types/functions: `arch_get_error`, `is_negated_errno`, `xtensa_regs.a`, and status register index `windowbase * 4 + 2`.
Control flow: reads the current window's a2-equivalent register and treats negated errno values as errors when requested. State and persistence behavior: writes `tcp->u_rval` and `tcp->u_error` only.
Dependencies and integration points: syscall exit processing. Risks: wrong window register selection corrupts every return value. Test signals: Xtensa success/error syscall traces across register-window configurations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/get_error.c -->
