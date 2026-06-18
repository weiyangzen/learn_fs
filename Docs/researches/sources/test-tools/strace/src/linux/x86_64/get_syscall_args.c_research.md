<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/x86_64/get_syscall_args.c

Purpose: fills `tcp->u_arg` from x86 syscall argument registers.
Important APIs/types/functions: `arch_get_syscall_args`, `tcp_sysent`, `COMPAT_SYSCALL_TYPES`, `x86_64_regs`, and `i386_regs`.
Control flow: x86_64/x32 uses `rdi,rsi,rdx,r10,r8,r9`; compat x32 syscalls zero-extend 32-bit arguments; i386 uses `ebx,ecx,edx,esi,edi,ebp` and zero-extends.
State and persistence behavior: writes the current syscall argument array only. Dependencies and integration points: every syscall decoder consumes these values.
Risks: sign extension is intentionally deferred to handlers; handlers that forget `truncate_klong_to_current_wordsize` can misprint signed compat arguments. Test signals: argument-order tests, x32 signed argument tests, and six-argument syscall fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/get_syscall_args.c -->
