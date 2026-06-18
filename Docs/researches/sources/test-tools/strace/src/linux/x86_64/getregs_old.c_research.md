<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/getregs_old.c -->
# sources/test-tools/strace/src/linux/x86_64/getregs_old.c

Purpose: fallback register-fetch path using older `PTRACE_GETREGS` semantics on x86.
Important APIs/types/functions: `get_regs`, `ptrace(PTRACE_GETREGS)`, x86 register union, CS selector logic, and iovec length update.
Control flow: fetches the full x86_64 user register struct, then identifies 32-bit mode from `cs == 0x23` and shrinks `x86_io.iov_len` to the i386 layout when appropriate.
State and persistence behavior: updates static register union and iovec length. Dependencies and integration points: enabled by `getregs_old.h` when GETREGSET is unavailable.
Risks: segment selector heuristics are kernel/ABI sensitive. Test signals: fallback builds or forced old-getregs tests with 64-bit and 32-bit tracees.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/getregs_old.c -->
