# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/dfa.h

This header defines the deterministic regexp structures used by the bayes tokenizer.

`Dreinst` stores final/loop flags and a transition case table. `Dreprog` stores four start states for combinations of beginning-of-line and end-of-line context. `Drecase` maps a starting rune boundary to the next instruction.

It declares conversion, execution, read, and write functions: `dregcvt`, `dregexec`, `Breaddfa`, and `Bprintdfa`.
