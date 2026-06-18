# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/peep.c

Purpose: peephole and copy-propagation optimizer for backend instruction streams.

Core behavior:
- `peep` completes the `Reg` structure for instructions between existing CFG nodes, repeatedly removes redundant register moves, tries substitution propagation, and removes redundant sign/zero-extension moves.
- `excise` converts an instruction to `ANOP`.
- `uniqp`/`uniqs` detect unique predecessor/successor paths.
- `subprop` rewrites register substitutions backward to enable move elimination.
- `copyprop` and `copy1` propagate copies forward through the CFG.
- `copyu` classifies instruction use/set behavior for a target operand.
- `copyas`, `copyau`, `copyau1`, `copysub`, and `copysub1` handle direct and indirect operand substitution.

Integration points:
- Invoked by `regopt` after register painting unless disabled by debug flags.
- Uses instruction semantics from `v.out.h`.

Risks:
- `copyu` defaults unknown opcodes to read-alter-write, which is conservative but can limit optimization.
- New opcodes must be added to use/set classification or they will block propagation.
- Correctness depends on CFG uniqueness checks and call-clobber handling.
