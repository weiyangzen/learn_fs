# sources/test-tools/strace/src/linux/alpha/raw_syscall.h

Purpose: implements a minimal zero-argument raw syscall helper for `alpha`.

Important APIs/types/functions: raw_syscall_0, STRACE_RAW_SYSCALL_H, raw_syscall_0; notable register references include none in this file.

Control flow: loads the requested syscall number into the ABI register, executes the architecture trap instruction, records an error flag where the ABI exposes one, and returns the raw result register.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on inline assembly register constraints, trap instructions, clobber lists, and `kernel_ulong_t`.

Risks/test signals: incorrect constraints or clobbers can miscompile; test a harmless syscall such as getpid and an expected failing syscall on native hardware/toolchains.

Source-read signal: reviewed complete local file (31 lines).
