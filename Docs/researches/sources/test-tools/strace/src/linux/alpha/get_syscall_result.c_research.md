# sources/test-tools/strace/src/linux/alpha/get_syscall_result.c

Purpose: fetches result registers needed by `alpha` before generic syscall-exit decoding.

Important APIs/types/functions: get_syscall_result_regs; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: reads the return and error-indicator registers from ptrace into static globals and reports failure if either fetch fails.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test syscall exits for both success and failure, including ptrace read errors.

Source-read signal: reviewed complete local file (13 lines).
