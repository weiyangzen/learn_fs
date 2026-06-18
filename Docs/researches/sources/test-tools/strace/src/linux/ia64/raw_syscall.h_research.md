# sources/test-tools/strace/src/linux/ia64/raw_syscall.h

Purpose: implements a minimal zero-argument raw syscall helper for `ia64`.

Important APIs/types/functions: raw_syscall_0, STRACE_RAW_SYSCALL_H, raw_syscall_0; notable register references include r15, r8, r10, r28.

Control flow: loads the requested syscall number into the ABI register, executes the architecture trap instruction, records an error flag where the ABI exposes one, and returns the raw result register.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on inline assembly register constraints, trap instructions, clobber lists, and `kernel_ulong_t`.

Risks/test signals: incorrect constraints or clobbers can miscompile; test a harmless syscall such as getpid and an expected failing syscall on native hardware/toolchains.

Source-read signal: reviewed complete local file (41 lines).
