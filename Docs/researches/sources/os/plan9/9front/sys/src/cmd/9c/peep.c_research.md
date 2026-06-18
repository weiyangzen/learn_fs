# File Research: sources/os/plan9/9front/sys/src/cmd/9c/peep.c

Peephole optimizer for PowerPC64 compiler output.

Key behavior:
- Completes the `Reg` chain for instructions inserted after global register optimization.
- Repeatedly eliminates redundant register moves through `copyprop` and `subprop`.
- Canonicalizes zero constants/register-zero uses when `R0ISZERO` permits it.
- Removes redundant extension/move chains such as `MOVB/MOVH/MOVW x,R; same R,R`.
- Folds `CMP R,$0` followed by a conditional branch into a condition-code-setting arithmetic/logical instruction when safe.
- `copyu` classifies instruction effects on a register as use, set, read-alter-write, or untouched across integer, floating, compare, branch, call, return, and text instructions.
- Helpers `copyas`, `copyau`, `copyau1`, `copysub`, and `copysub1` detect and substitute direct/indirect register references.
- `uniqp`/`uniqs` restrict transformations to unique-predecessor/successor flow where required.
- Floating condition-code folding cases are present but disabled in comments.

Filesystem relevance: indirect compiler optimizer.
