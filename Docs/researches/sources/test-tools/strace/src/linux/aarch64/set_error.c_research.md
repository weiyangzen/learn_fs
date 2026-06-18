# sources/test-tools/strace/src/linux/aarch64/set_error.c

Purpose: injects a synthetic syscall error or success result into `aarch64` tracee registers.

Important APIs/types/functions: arch_set_error, arch_set_success; key state includes `struct tcb`, `tcp->scno`, `tcp->u_arg`, `tcp->u_rval`, `tcp->u_error`, and register fields regs[0].

Control flow: `arch_set_error` writes the architecture error convention from `tcp->u_error`; `arch_set_success` writes `tcp->u_rval`; implementations either poke individual user offsets or call `set_regs` after mutating the saved register block.

State/persistence behavior: mutates only the active trace control block and current ptrace register snapshot; any tracee register changes are applied immediately through ptrace helpers.

Dependencies/integration: participates in generic syscall enter/exit decoding; depends on ../arm/set_error.c.

Risks/test signals: Test with syscall fault injection for both success and errno paths, including ESRCH/disappearing-tracee behavior where relevant.

Source-read signal: reviewed complete local file (32 lines).
