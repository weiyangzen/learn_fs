<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_get_personality.c -->
# sources/test-tools/strace/src/linux/x86_64/arch_get_personality.c

Purpose: derives strace personality from `PTRACE_GET_SYSCALL_INFO` audit architecture and syscall number.
Important APIs/types/functions: `get_personality_from_syscall_info`, `struct_ptrace_syscall_info`, `AUDIT_ARCH_I386`, `__X32_SYSCALL_BIT`, and x32 build guard.
Control flow: starts as i386 when audit arch says i386; otherwise requires entry/seccomp syscall-info operations, inspects x32 syscall bit for non-negative syscall numbers, and returns -1 for unsupported operation states.
State and persistence behavior: stateless helper. Dependencies and integration points: used when syscall info is available instead of older register-based personality selection.
Risks: syscall number -1 under seccomp must not be misclassified as x32. Test signals: PTRACE_SYSCALL_INFO tests for x86_64, i386, x32, and seccomp errno cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_get_personality.c -->
