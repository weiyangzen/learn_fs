# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/branch.c

PowerPC branch and condition-register instruction emulation for `qi`.

Key responsibilities:
- Defines opcode table for primary opcode 19 extended branch/CR operations.
- Decodes branch option/condition names for trace output.
- Implements conditional branch decision logic using CTR and CR bits.
- Emulates branch-to-CTR, branch-to-LR, conditional immediate branches, absolute/relative branches, link-register updates, and PC adjustment.
- Implements CR logical operations and `mcrf`.
- Emits optional call-tree tracing for calls and returns.
- Treats `isync` as a traceable no-op.

Dependencies:
- Uses decode macros, register state, condition bits, tracing, and symbol helpers from `power.h`.

Notable risks:
- Branches update `reg.pc` to target minus 4 because the dispatcher adds 4 after execution.
- `condok()` decrements CTR and validates reserved fields, so branch option semantics are centralized and fragile.
- Return/call tracing is observational and does not affect execution semantics.
