# sources/test-tools/strace/src/linux/x32/ptrace_pokeuser.c

## Purpose
Implements the x32-specific backend for writing tracee user-register slots through `PTRACE_POKEUSER`. It works around a kernel x32 limitation by issuing the raw x86_64 syscall rather than relying on the libc syscall ABI selected for an x32 build.

## Important APIs, Types, And Functions
Defines `static long ptrace_pokeuser(int pid, unsigned long off, kernel_ulong_t val)`. Inputs are the tracee PID, a user-area byte offset, and the machine-width value to write. It calls `syscall(101, PTRACE_POKEUSER, pid, off, val)`, where syscall number 101 is the x86_64 `ptrace` syscall number. It depends on `kernel_ulong_t`, `PTRACE_POKEUSER`, and the generic `syscall` entry point.

## Control Flow
The function is a straight-line wrapper: receive arguments, call raw x86_64 syscall 101 with `PTRACE_POKEUSER`, and return the syscall result. Error handling is deliberately left to the caller. In the integration path, `upoke.c` includes this file, calls `ptrace_pokeuser`, reports non-`ESRCH` errors, and returns `-1` on failure.

## State And Persistence
The function has no local static state. Its only persistent effect is external: on success it mutates the traced process's user-register area through ptrace. That mutation is immediately visible to subsequent ptrace register reads and to the tracee when execution resumes.

## Dependencies And Integration Points
Integrated by `sources/test-tools/strace/src/upoke.c`, which provides the public `upoke(struct tcb *, unsigned long, kernel_ulong_t)` helper. That helper is used by x32/x86_64 register mutation paths such as `set_scno.c` and `set_error.c`. This file's architecture-specific behavior is required because the normal x32 `PTRACE_POKEUSER` path is described as crippled from the initial x32 kernel support commit.

## Risks
Hard-coding syscall number 101 is intentional for x86_64 but fragile if reused outside this architecture path. The function bypasses libc's `ptrace` wrapper, so argument ordering and widths must remain exactly compatible with the x86_64 kernel ABI. Incorrect offsets from callers can corrupt the wrong register slot. Tracee exit races still surface as syscall errors and must be handled by `upoke`.

## Test Signals
Fault-injection tests that modify syscall numbers or return values on x32 should exercise this path indirectly. Direct signals include successful `upoke` calls against `RAX`/`ORIG_RAX` offsets and expected `ESRCH` tolerance when a tracee disappears. Cross-check with x86_64 register mutation tests helps ensure the raw syscall workaround behaves like the normal ptrace wrapper.

## Source-Read Signal
Reviewed the complete local file, including the explanatory comment and the single wrapper implementation.
