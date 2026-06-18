# sources/test-tools/strace/src/linux/avr32/get_scno.c

Purpose: extracts the current syscall number for the `avr32` backend.

Important APIs/types/functions: arch_get_scno; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields r8.

Control flow: on syscall entry it reads the ABI syscall-number register or user offset, may perform sanity checks for stray exits, then stores the result in `tcp->scno` and returns the generic status code.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on architecture register globals, ptrace helpers, and common tcb fields.

Risks/test signals: Test with representative syscall entries, invalid/out-of-range numbers, and personality-specific numbering when present.

Source-read signal: reviewed complete local file (14 lines).
