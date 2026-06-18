# File Research: sources/os/plan9/plan9/sys/src/9/kw/lproc.s

## Role

Small ARM process transition assembly for entering user mode and returning from fork.

This is process-control infrastructure, not filesystem code.

## Main Interfaces

- `touser(SB)`: enters user mode at a supplied user entry PC.
- `forkret(SB)`: returns from a forked process into scheduler/user restore flow.

## Important Behavior

- `touser` sets up CPSR/SPSR state for user execution, loads the user stack pointer, and exception-returns into user mode.
- `forkret` loads the current process saved scheduler label, clears the process pointer in `m->proc`, and jumps through `gotolabel`.

## Dependencies And Assumptions

- Includes `mem.h` and `arm.h`.
- Assumes `Mach`/`Proc` offsets used in assembly match `dat.h`.
- Relies on Plan 9 ARM exception return conventions.

## Notable Risks

- Offset drift between assembly and C structs would break context switching.
