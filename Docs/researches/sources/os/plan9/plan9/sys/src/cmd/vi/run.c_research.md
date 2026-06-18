# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/run.c

Purpose: Main integer/control-flow instruction interpreter for MIPS.

Key behavior:
- Defines the primary opcode dispatch table.
- `run` repeatedly fetches, dispatches, advances PC, checks instruction breakpoints, and optionally traces registers.
- Implements loads/stores, arithmetic/logical immediates, jumps, branches, branch-likely variants, LL/SC as load/store, and `bcond` variants.
- Executes MIPS delay slots explicitly on taken branches and jumps.
- Tracks instruction counts and branch delay-slot usage.

Dependencies:
- Uses register state, memory accessors, special/COP1/syscall dispatch, breakpoints, tracing, and decode macros.

Notable details:
- Undefined opcodes print a trap and return to the command loop via `longjmp`.
