# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_process_lwpstatus.c

## Purpose
Implements ptrace/process helpers for reading LWP status and register sets, including compat-netbsd32 register layout handling.

## Main Interfaces
- `ptrace_read_lwpstatus`, `process_read_lwpstatus`: fill `ptrace_lwpstatus` from an LWP.
- `ptrace_update_lwp`: switch a held target LWP reference to a requested LID.
- `process_validregs`, `process_validfpregs`, `process_validdbregs`: validate register access availability and reject system LWPs.
- `process_doregs`, `process_dofpregs`, `process_dodbregs`: read/write general, floating-point, and debug registers via `uio`.
- `proc_regio`: common register-buffer transfer helper when register ptrace support is compiled in.

## State And Control Flow
LWP status includes LID, signal mask, pending signal set, LWP name, and private pointer. Register I/O reads the machine register set into a kernel buffer, transfers the requested slice with `uiomove`, and writes back only for `UIO_WRITE` if the target LWP is stopped.

## Dependencies And Integration
Integrates with machine `process_read_*`/`process_write_*` register functions, ptrace ABI structures, LWP references/locks, compat-netbsd32 type selection, and `uio` transfer mechanics.

## Risks And Edge Cases
- `ptrace_update_lwp` drops and reacquires LWP references under the process lock and rejects system LWPs.
- A 32-bit tracer is blocked from tracing a 64-bit target register image.
- Register writes require `LSSTOP`; otherwise `EBUSY`.
- `proc_regio` bounds offsets and kernel scratch-buffer size to avoid overrun.

## Filesystem Relevance
Low. Debugger register/status support does not implement filesystem behavior.
