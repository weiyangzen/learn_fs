# sources/test-tools/strace/src/linux/aarch64/get_syscall_args.c

Purpose: copies syscall arguments from `aarch64` register state or backing register-stack memory into `tcp->u_arg`.

Important APIs/types/functions: arch_get_syscall_args; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields regs[0], regs[1], regs[2], regs[3], regs[4], regs[5].

Control flow: after the syscall number is known, it reads up to `n_args(tcp)` or `MAX_ARGS` arguments from ABI-defined registers, compatibility helper code, or memory addresses derived from register-stack state, returning `1` on success or `-1` on fatal fetch failure.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on ../arm/get_syscall_args.c.

Risks/test signals: Test with six-argument syscalls, compatibility personalities, and ptrace permission/fault cases for memory-backed argument locations.

Source-read signal: reviewed complete local file (25 lines).
