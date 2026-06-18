# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/dfa.h

- Role: Public interface and data layout for deterministic regexp programs.
- Key types: `Dreprog` with four start states, `Dreinst` with final/loop/case array, and `Drecase` with range start and next state.
- Key declarations: `dregcvt`, `dregexec`, `Breaddfa`, `Bprintdfa`.
- Integration: Included by DFA compiler, dumper, regex generator, and message tokenizer.
