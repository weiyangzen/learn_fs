# File Research: sources/os/plan9/9front/sys/src/cmd/spin/dstep.c

`dstep.c` generates verifier C code for Promela `d_step` sequences in Spin. It turns deterministic step blocks into straight-line/generated-label code, while preserving executability checks, state reachability marking, and correct exits back to surrounding control flow.

`putcode()` is the external entry point. It emits guard checks for the first statement or selection, marks reached states, handles `TstOnly` enabledness calls, saves state with `sv_save()`, then delegates to `putCode()` for the sequence body. `CollectGuards()` recursively emits disjunctions for `if`/`do` options, sends, receives, conditions, and `else`.

The file tracks generated label sources and destinations with `Tojump[]`, `Jumpto[]`, and `Special[]`. `Sourced()`, `Dested()`, `FirstTime()`, and `Mopup()` prevent duplicate labels, report gotos that leave a `d_step`, preserve global exit labels, and emit a break destination label when required.

`filterbad()` rejects constructs that cannot safely live inside `d_step`: process termination, nested `d_step`/`atomic`, `run` operators, and remote references. `putCode()` handles nested non-atomic fragments, break/goto translation, guard options, generated `Uerror()` calls for blocking selections, and transitions to the next element.

Important coupling: depends on Spin’s `Element`, `Sequence`, `SeqList`, code-emission functions such as `putstmnt()`, label resolution through `get_lab()`/`huntele()`, process IDs, claim detection, and global verifier output files. Capacity is capped by `MAXDSTEP`; oversized or confusing control structures abort generation.
