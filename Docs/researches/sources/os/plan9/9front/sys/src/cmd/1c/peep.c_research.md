# File Research: sources/os/plan9/9front/sys/src/cmd/1c/peep.c

Peephole and local copy-propagation optimizer for `1c`.

Key responsibilities:
- Completes the `Reg` flow structure by inserting flow nodes for raw `Prog` instructions between existing nodes.
- Repeatedly propagates register-to-register moves and removes redundant moves using `copyprop` and `subprop`.
- Folds address-register add/sub increments into 68000 auto-increment or predecrement addressing modes.
- Removes unnecessary condition-code save/restore pairs.
- Removes redundant `TST` instructions when prior condition-code settings are equivalent.
- Rewrites the pattern `TSTB (A); BLT/GE; ORB $128,(A)` into `TAS (A)` where legal.
- Provides operand compatibility, use/set classification, copy substitution, and instruction-size helpers.

Notable details:
- Conservative handling exists for divide, subroutine calls, partial-register writes, return registers, and FP/address registers.
- Many decisions depend on 68000 condition-code behavior and addressing-mode legality.
