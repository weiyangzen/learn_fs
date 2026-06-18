<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_set_syscall_info.c -->
## sources/test-tools/strace/src/disable_ptrace_set_syscall_info.c

Purpose: Specializes the ptrace-disabling helper to reject only `PTRACE_SET_SYSCALL_INFO`.

Important APIs and types: Defines `DISABLE_PTRACE_REQUEST PTRACE_SET_SYSCALL_INFO` and helper invocation name before including `disable_ptrace_request.c`.

Control flow: Runtime behavior is the shared seccomp-template flow: install a filter that blocks ptrace when the first argument matches `PTRACE_SET_SYSCALL_INFO`, then exec the requested program.

State and persistence: No local state.

Dependencies and integration: Used by tests that verify strace behavior when syscall-info setting is unavailable.

Risks: Depends on platform request macro availability and the shared template's BPF argument matching.

Test signals: Tests should show only `PTRACE_SET_SYSCALL_INFO` receives the configured errno and other ptrace requests are not rejected by this helper.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_set_syscall_info.c -->
