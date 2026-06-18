<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/get_scno.c -->
# sources/test-tools/strace/src/linux/x86_64/get_scno.c

Purpose: extracts syscall number and selects x86_64, i386, or x32 personality from registers.
Important APIs/types/functions: `arch_get_scno`, `x86_io.iov_len`, `orig_eax`, `orig_rax`, `__X32_SYSCALL_BIT`, and `update_personality`.
Control flow: i386 is detected by regset size; otherwise the x32 syscall bit selects x32 unless the number is -1 from seccomp errno handling. x32-native builds reject unsupported 64-bit mode.
State and persistence behavior: updates `tcp->scno` and current personality. Dependencies and integration points: central syscall dispatch path.
Risks: personality misclassification points at the wrong syscall table and argument ABI. Test signals: mixed-ABI exec tests and seccomp `orig_rax == -1` regression tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/get_scno.c -->
