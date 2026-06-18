<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace.c -->
## sources/test-tools/strace/src/disable_ptrace.c

Purpose: Builds a helper executable that runs a program with the entire `ptrace` syscall rejected with `EPERM`.

Important APIs and types: Defines `DISABLE_PTRACE_ERRNO EPERM`, `DEFAULT_PROGRAM_INVOCATION_NAME`, then includes `disable_ptrace_request.c`.

Control flow: All runtime flow comes from the included template: initialize program name, install a seccomp filter rejecting ptrace, then `execvp` the target.

State and persistence: No separate state beyond the included template.

Dependencies and integration: This is a specialization wrapper for strace tests that need ptrace unavailable.

Risks: Macro-driven include style means changes in `disable_ptrace_request.c` affect this helper directly.

Test signals: Tests should assert ptrace fails with `EPERM` while non-ptrace syscalls and exec of target continue.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace.c -->
