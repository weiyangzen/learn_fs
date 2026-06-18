# File Research: sources/os/plan9/9front/sys/src/cmd/7c/peep.c

Peephole optimizer for emitted ARM64 backend instructions. It completes the `Reg` chain for inserted instructions, then repeatedly performs local copy/constant/store propagation, redundant move removal, selected opcode simplification, and simple instruction scheduling.

Key active behavior:
- `peep` inserts missing `Reg` nodes for instructions added after global register optimization.
- Propagates stores to later loads from the same local variable through `storeprop`.
- Simplifies redundant sign/zero-extension moves when prior definitions already have the right width.
- Runs copy propagation through `copyprop`, `copy1`, `copyu`, `copyas`, `copyau`, and substitution helpers.
- Runs constant propagation from constant-to-register moves through `constprop`.
- Converts `EOR -1,x,y` into `MVN x,y` forms.
- Removes duplicate extension/move chains such as `MOVB x,R; MOVB R,R`.
- Performs a small load scheduling transform by swapping an independent instruction between a load and the first consumer.

Key helper logic:
- `independent` checks whether two instructions can be swapped without register or memory hazards.
- `subprop` tries register substitution around copies so one copy can later disappear.
- `shiftprop` can fold a shift into a `D_SHIFT` operand, but the top-level call is disabled with `if(0 && shiftprop(r))`.
- `regzer` is currently disabled by an early `return 0`, so zero-register canonicalization is inactive.
- `xtramodes` and predicate conversion logic are compiled out under `NOTYET`/`XXX`.

Predicate-related dead/disabled code:
- Defines conditional branch metadata, predicability checks, CPSR modification checks, join/split analysis, and `predicate`, but the actual call is disabled.
- `modifiescpsr` currently returns true unconditionally before checking opcodes, which would make predicate analysis conservative if enabled.

Filesystem relevance: indirect compiler optimizer.
