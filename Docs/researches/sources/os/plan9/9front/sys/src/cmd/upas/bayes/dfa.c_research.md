# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/dfa.c

This file converts Plan 9 regexp programs (`Reprog`) into minimized deterministic regexp programs (`Dreprog`) and executes or serializes them. It is used by the mail tokenizer for fast repeated matching.

`dregcvt()` counts NFA instructions, computes “interesting” rune boundaries, builds subset-construction states (`Reiset`), follows empty transitions, creates transitions for beginning/end-of-line contexts, minimizes by partition refinement, and emits a compact `Dreprog`.

`dregexec()` runs the DFA and returns the best match length from a string position. `Bprintdfa()` serializes a DFA in text form, while `Breaddfa()` reads that format back with strict error handling. Optional `DUMP` code can print internal DFA structure for debugging.
