# File Research: sources/os/bsd/netbsd-src/sys/sys/ptrace.h

## Purpose
Defines ptrace request numbers, event masks, I/O and LWP status structures, signal-info transport, userland declaration, and kernel ptrace/machine-register support hooks.

## Main API
- Requests: `PT_TRACE_ME`, `PT_READ_I`, `PT_READ_D`, `PT_WRITE_I`, `PT_WRITE_D`, `PT_CONTINUE`, `PT_KILL`, `PT_ATTACH`, `PT_DETACH`, `PT_IO`, `PT_DUMPCORE`, `PT_SYSCALL`, `PT_SYSCALLEMU`, event/siginfo/LWP requests, and machine-dependent range from `PT_FIRSTMACH`.
- Structures: `ptrace_event_t`, `ptrace_state_t`, `struct ptrace_io_desc`, optional legacy `struct ptrace_lwpinfo`, `struct ptrace_lwpstatus`, `ptrace_siginfo_t`.
- Event bits: `PTRACE_FORK`, `PTRACE_VFORK`, `PTRACE_VFORK_DONE`, `PTRACE_LWP_CREATE`, `PTRACE_LWP_EXIT`, `PTRACE_POSIX_SPAWN`.
- I/O operations: `PIOD_READ_D`, `PIOD_WRITE_D`, `PIOD_READ_I`, `PIOD_WRITE_I`, `PIOD_READ_AUXV`.
- Kernel methods: `struct ptrace_methods`.
- Kernel helpers: `ptrace_update_lwp`, `ptrace_hooks`, `process_doregs`, `process_dofpregs`, `process_dodbregs`, `process_domem`, `do_ptrace`, register read/write hooks, `ptrace_machdep_dorequest`.
- Userland: `ptrace`.

## Dependencies
Includes signal and siginfo headers plus `machine/ptrace.h`; kernel compatibility can include netbsd32 definitions.

## Risks and Notes
The header preserves obsolete `PT_LWPINFO` under legacy/kernel conditions. 32/64-bit process register type aliases are carefully conditional for compat kernels. Machine-dependent requests and register support are optional.
