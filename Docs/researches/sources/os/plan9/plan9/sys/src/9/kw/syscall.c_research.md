# File Research: sources/os/plan9/plan9/sys/src/9/kw/syscall.c

## Role

ARM syscall and notify handling for the Kirkwood kernel. It dispatches system calls, manages user notification return, prepares exec/fork register state, and records syscall tracing/profiling metadata.

This is kernel process ABI code. It supports filesystem syscalls through the shared Plan 9 syscall table but does not implement filesystem operations itself.

## Main Interfaces

- `syscall(Ureg *ureg)`: main syscall dispatcher.
- `notify(Ureg *ureg)`: prepares user notification delivery.
- `noted(Ureg *cur, uintptr arg0)`: handles `noted` return modes.
- `execregs`
- `sysprocsetup`
- `forkchild`

## Important Behavior

- Extracts syscall number and arguments from user register/stack state.
- Validates user memory for syscall arguments.
- Calls `systab[scallnr]`.
- Handles Plan 9 error unwinding through `waserror`/`nexterror`.
- Supports syscall tracing through `syscallfmt`/`sysretfmt`.
- `notify` builds a user stack frame containing saved registers and note string.
- `noted` supports `NCONT`, `NRSTR`, `NSAVE`, and `NDFLT`.
- `execregs` initializes user stack, PC, and return registers for a new image.
- `forkchild` copies a parent `Ureg` and makes child return zero.

## Dependencies And Assumptions

- Depends on `../port/systab.h`, `tos.h`, and port process code.
- Assumes ARM `Ureg` layout and syscall ABI.
- Uses `validaddr`, `validalign`, and `evenaddr`.

## Notable Risks

- User stack/register manipulation is ABI-sensitive.
- Incorrect validation around user pointers would affect every syscall, including filesystem syscalls.
