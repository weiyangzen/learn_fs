# File Research: sources/os/plan9/plan9/sys/src/cmd/grep/sub.c

This file provides allocation and regex construction helpers. `mal` is an arena allocator based on `sbrk`; `sal` allocates DFA states; `ral` allocates regex nodes and tracks maximum follow-set size.

It optimizes large OR/class structures into `Tcase` byte dispatch tables via `addcase`, `countor`, and `case1`.

It also implements pattern parsing entry `str2top`, input character retrieval `getrec`, regex fragment combinators (`re2cat`, `re2star`, `re2or`, `re2char`), and debug regex printing.

The allocator and code style are tightly bound to Plan 9-era assumptions.
