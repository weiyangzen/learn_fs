<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_get_syscall_info.c -->
## sources/test-tools/strace/src/disable_ptrace_get_syscall_info.c

Purpose: Specializes the ptrace-disabling helper to reject only `PTRACE_GET_SYSCALL_INFO`.

Important APIs and types: Defines `DISABLE_PTRACE_REQUEST PTRACE_GET_SYSCALL_INFO` and helper invocation name before including `disable_ptrace_request.c`.

Control flow: Runtime flow is inherited from the template; its seccomp filter compares ptrace request argument against `PTRACE_GET_SYSCALL_INFO` and returns errno only for that request.

State and persistence: No local state.

Dependencies and integration: Used by tests for fallback behavior when `PTRACE_GET_SYSCALL_INFO` is unavailable or blocked.

Risks: Requires the target platform to define the request value through included ptrace headers.

Test signals: Tests should show `PTRACE_GET_SYSCALL_INFO` fails while other ptrace requests can still pass the filter.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_get_syscall_info.c -->
