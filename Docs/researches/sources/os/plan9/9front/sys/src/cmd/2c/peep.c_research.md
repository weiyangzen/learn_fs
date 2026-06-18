# File Research: sources/os/plan9/9front/sys/src/cmd/2c/peep.c

Purpose: peephole and local dataflow optimizer over the compiler’s `Reg` CFG.

Key behavior:
- `peep()` first fills missing `Reg` nodes for non-pseudo instructions between optimizer CFG nodes.
- Repeatedly performs copy propagation and substitution propagation for `MOVL`, `FMOVEF`, and `FMOVED`, deleting redundant moves as `ANOP`.
- Folds `(A)` plus nearby `AADDL/ASUBL` into 68020 autoincrement/autodecrement addressing where safe.
- Removes redundant CCR save/restore pairs and redundant `TST` instructions whose condition codes are already established.
- Recognizes `TSTB (A); BLT/GE; ORB $128,(A)`-style idiom and turns it into `TAS`.
- Helper routines classify instruction sizes, condition-code behavior, register/reference usage, direct/indirect operand equivalence, and substitution legality.

Research notes:
- Copy propagation is conservative around calls, divide instructions, returns, read-alter-write instructions, address registers, and split control-flow merges.
- `excise()` does not remove nodes immediately; it rewrites programs to `ANOP`, later cleaned by `regopt()`.
