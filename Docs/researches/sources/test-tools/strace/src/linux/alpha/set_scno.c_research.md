# sources/test-tools/strace/src/linux/alpha/set_scno.c

Purpose: updates the tracee syscall number for `alpha` syscall tampering/restart support.

Important APIs/types/functions: arch_set_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields defined by included architecture helpers.

Control flow: writes the requested syscall number into the architecture orig-syscall register using `upoke`, `set_regs`, or an architecture regset such as `NT_ARM_SYSTEM_CALL`.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test by rewriting a syscall number under ptrace and confirming the kernel executes/prints the replacement call.

Source-read signal: reviewed complete local file (12 lines).
