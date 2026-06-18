# File Research: sources/os/plan9/9front/sys/src/cmd/tc/peep.c

Performs peephole and copy/constant propagation over backend register-flow nodes.

Key points:
- `peep` completes missing `Reg` nodes between optimizer blocks, repeatedly eliminates redundant register moves via copy propagation, applies substitution propagation, folds constant moves, rewrites `EOR -1,x,y` to `MVN x,y`, and removes redundant repeated byte/halfword extension moves.
- `excise` turns an instruction into `NOP`.
- `uniqp` and `uniqs` detect unique predecessor/successor paths.
- `subprop` rewrites register copy direction through a basic path to make later copy elimination possible.
- `copyprop` and `copy1` implement the main copy-propagation data walk.
- `constprop` replaces repeated identical constants with register references until the register is clobbered or control merges.
- `copyu` classifies instruction use/set behavior for registers and constants across moves, arithmetic, branches, calls, returns, and `MOVM`.
- `copyas`, `copyau`, `copyau1`, `copysub`, and `copysub1` perform address equality, address-use checks, and substitution.

Dependencies and interactions:
- Operates on `Reg` graph built by `reg.c`.
- Uses backend opcodes/address classes from `gc.h`.

Research relevance:
- This is the late local optimizer for removing redundant Thumb instructions after global register optimization.
