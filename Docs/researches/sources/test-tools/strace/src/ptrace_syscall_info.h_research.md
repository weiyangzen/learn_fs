# sources/test-tools/strace/src/ptrace_syscall_info.h

Purpose: Declares ptrace syscall-info feature flags, probes, and printer for use by core ptrace decoding.

Important APIs/types/functions: extern booleans for GET/SET support, `test_ptrace_get_syscall_info`, `test_ptrace_set_syscall_info`, and `print_ptrace_syscall_info`.

Control flow: header-only declarations; implementation handles probing and partial printing.

State and persistence: declares state owned by `ptrace_syscall_info.c`.

Dependencies/integration: included by `ptrace.c` and startup/initialization logic that decides whether to use new ptrace APIs.

Risks: prototypes must match implementation and availability guards in `ptrace.h`; wrong linkage would break optional feature detection.

Test signals: successful full build with and without syscall-info UAPI support and ptrace syscall-info decoder tests.
