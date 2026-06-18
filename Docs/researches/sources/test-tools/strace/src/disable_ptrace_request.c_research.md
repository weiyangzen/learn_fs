<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_request.c -->
## sources/test-tools/strace/src/disable_ptrace_request.c

Purpose: Template implementation for helper executables that run a target program under a seccomp filter rejecting `ptrace` or a specific ptrace request.

Important APIs and types: `die`, `init`, optional `get_arch`, and `main`. Uses `struct sock_filter`, `struct sock_fprog`, `struct seccomp_data`, ptrace request macros, and `DISABLE_PTRACE_REQUEST`/`DISABLE_PTRACE_ERRNO` specialization macros.

Control flow: `init` sets `program_invocation_name`. When required kernel features are present, `main` validates arguments, enables `PR_SET_NO_NEW_PRIVS`, builds a classic BPF filter that matches architecture, syscall number `__NR_ptrace`, and optionally first ptrace argument, returns `SECCOMP_RET_ERRNO | errno` for the rejected case, installs the filter with `PR_SET_SECCOMP`, then `execvp`s the target. `get_arch` forks and traces a child to discover the audit architecture via `PTRACE_GET_SYSCALL_INFO`. Unsupported builds compile a `main` that errors out.

State and persistence: No long-lived state after exec. Uses forked child only during architecture discovery.

Dependencies and integration: Depends on `defs.h`, `ptrace.h`, `scno.h`, signal/wait/prctl headers, Linux filter/seccomp headers, and wrapper macros from including files.

Risks: The helper itself uses ptrace before installing seccomp; if `PTRACE_GET_SYSCALL_INFO` is unavailable, it exits. BPF argument endianness handling for `args[0]` is critical. Macro inclusion makes each wrapper a separate compiled program.

Test signals: Tests should cover no-argument failure, unsupported-feature build, full ptrace rejection, single-request rejection, errno selection, successful target exec, and architecture mismatch allow path.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_request.c -->
