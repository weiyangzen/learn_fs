# sources/test-tools/strace/src/linux/ia64/get_error.c

Purpose: translates the `ia64` syscall return/error convention into `tcp->u_rval` and `tcp->u_error`.

Important APIs/types/functions: arch_get_error; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields gr[10], gr[8].

Control flow: on syscall exit it reads the architecture return/error register convention, optionally checks negated errno ranges or dedicated error flags, sets `u_rval=-1` for errors, and otherwise records the raw return value.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on negated_errno.h.

Risks/test signals: Test with successful syscalls, negated errno returns, and any architecture-specific dedicated error register path.

Source-read signal: reviewed complete local file (19 lines).
