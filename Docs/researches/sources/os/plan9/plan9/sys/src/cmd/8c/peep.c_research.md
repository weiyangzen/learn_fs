# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/peep.c

## Purpose
Implements peephole and local copy-propagation optimizations over the backend control-flow graph.

## Key Functions
- `peep()` inserts missing `Reg` nodes for non-data instructions, then repeatedly applies optimizations.
- `needc()` checks whether later code needs carry flags before rewriting add/sub into inc/dec.
- `excise()` turns an instruction into `ANOP`.
- `uniqp()` / `uniqs()` find unique predecessor/successor nodes.
- `regtyp()` identifies general-purpose register operands.
- `subprop()` performs substitution propagation across move chains.
- `copyprop()` and `copy1()` remove redundant register copies when safe.
- `copyu()` classifies whether an instruction uses, sets, read-modify-writes, or ignores an operand.
- `copyas()`, `copyau()`, `copysub()` compare and substitute operands.

## Important Behavior
- Eliminates redundant `MOVL reg,reg` and propagated register copies.
- Converts `ADD/SUB $1` and `$-1` to `INC/DEC` only if carry flags are not needed.
- Simplifies chains of sign/zero extension moves when followed by matching extensions.
- Treats special x86 instructions conservatively because many implicitly use `AX`, `DX`, `CX`, `SI`, or `DI`.

## Research Notes
This optimizer is deliberately instruction-semantics-aware; incorrect `copyu()` classification would create miscompilations.
