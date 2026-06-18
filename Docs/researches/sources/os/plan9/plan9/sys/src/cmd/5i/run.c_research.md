# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/run.c

## Scope

ARM instruction dispatch and execution engine for `5i`.

## Behavior

- Defines the `itab[]` decode-class table for data processing, multiply, swap, load/store, block transfer, branch, branch-link, syscall, and multiply-long classes.
- `run()` fetches, decodes, tests condition codes, executes handlers, advances PC, and checks instruction breakpoints.
- Implements ARM condition evaluation using remembered compare/test operands.
- Implements shifts, ALU operations, multiply/multiply-accumulate, long multiply, swap, word/byte/halfword memory transfers, block load/store, branches, and call tracing.

## Dependencies

Uses `armclass()` from Mach support, memory APIs from `mem.c`, syscall dispatch from `syscall.c`, and symbol helpers for call tracing.

## Risks And Invariants

- Several ARM operations are deliberately unsupported and call `undef()`, including ADC/SBC/RSC and some LDM/STM modes.
- Carry/condition modeling is partial and based on later condition evaluation from saved operands.
- Instruction table indexes depend on external `armclass()` matching the exact table layout.
