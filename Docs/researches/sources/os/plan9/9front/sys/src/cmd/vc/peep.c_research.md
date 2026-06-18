# File Research: sources/os/plan9/9front/sys/src/cmd/vc/peep.c

Purpose: Peephole and copy-propagation optimization for generated MIPS `Prog` streams.

Key behavior:
- Completes the `Reg` flow graph for instructions inserted between register optimizer nodes.
- Repeatedly removes redundant register-to-register moves through `copyprop` and `subprop`.
- Converts zero constants to `R0` when profitable and attempts propagation again.
- Removes redundant sign/zero-extension sequences like `MOVB x,R; MOVB R,R`.
- `copy1` walks control flow to substitute source registers while respecting merge points, sets, calls, and read-alter-write hazards.
- `copyu`, `copyau`, `copyas`, and substitution helpers classify and rewrite register uses in instruction operands.

Dependencies:
- Uses `gc.h`, `Reg` graph links, address classes from `v.out.h`, and `excise` by replacing instructions with `ANOP`.

Notable details:
- Calls and returns conservatively block propagation for calling-convention registers.
