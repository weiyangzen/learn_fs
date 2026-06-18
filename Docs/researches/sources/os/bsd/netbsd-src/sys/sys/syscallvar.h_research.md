# File Research: sources/os/bsd/netbsd-src/sys/sys/syscallvar.h

This kernel-only header defines runtime syscall dispatch helpers and syscall package registration.

Key interface details:
- Errors out for non-kernel inclusion.
- Optionally includes DTrace configuration via `opt_dtrace.h`.
- Includes `<sys/systm.h>` and `<sys/proc.h>`.
- Declares `emul_netbsd`.
- Defines `struct syscall_package` with syscall code, flags, and handler pointer.
- Declares `syscall_init`, `syscall_establish`, and `syscall_disestablish`.
- `sy_call()` sets `l->l_sysent`, calls the syscall handler, then clears `l->l_sysent`.
- `sy_invoke()` wraps syscall invocation with trace/DTrace entry and return hooks, initializes return values, and handles architecture-specific return-register behavior.
- Declares `syscallnames[]` and `altsyscallnames[]`.

Research notes:
- This is the kernel dispatch integration point for syscall tables and emulation packages.
- `sy_invoke()` is where tracing and DTrace hooks are composed with normal syscall execution.
- The return-value initialization is architecture-sensitive; mips and m68k preserve the second return register for compatibility reasons.
