# sources/test-tools/strace/src/ptrace_syscall_info.c

Purpose: Detects kernel support for `PTRACE_GET_SYSCALL_INFO`/`PTRACE_SET_SYSCALL_INFO` and prints `struct ptrace_syscall_info` safely for partial kernel/user lengths.

Important APIs/types/functions: globals `ptrace_get_syscall_info_supported` and `ptrace_set_syscall_info_supported`; probes `test_ptrace_get_syscall_info`, `test_ptrace_set_syscall_info`; printer `print_ptrace_syscall_info`; helpers `print_psi_entry`, `print_psi_seccomp`, `print_psi_exit`.

Control flow: when `HAVE_FORK` is available, support tests fork a tracee, use `PTRACE_TRACEME`, `PTRACE_O_TRACESYSGOOD`, and syscall stops to verify NONE/ENTRY/EXIT semantics and, for SET, mutation of syscall numbers, args, and return values. Printing fetches `MIN(user_len, kernel_len, sizeof(info))`, then progressively prints only fields present in the fetched size and dispatches by `info.op`.

State and persistence: maintains global booleans caching feature support for the process. Test tracees and pipes are transient and killed/closed in cleanup paths.

Dependencies/integration: uses ptrace, wait, fork, signal, syscall number definitions, audit arch xlat, `kill_save_errno`, `scno.h`, and `ptrace_syscall_info_op`. Called by startup feature checks and `ptrace.c`.

Risks: probes execute real tracee syscalls and are architecture-sensitive; NOMMU leaves defaults unchanged. Partial-structure printing must avoid reading absent fields. s390 masks syscall numbers to 16 bits. SET probes deliberately rewrite tracee execution, so cleanup paths must reliably kill/wait tracees.

Test signals: startup debug messages, kernels with/without GET/SET support, partial user lengths, seccomp op printing, entry/exit error return rendering, and fork-disabled configurations.
