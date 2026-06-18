# File Research: sources/os/plan9/plan9/sys/src/cmd/grep/comp.c

This file implements the incremental regex automaton compiler for Plan 9 `grep`. `increment` computes the next DFA state for a state/input byte by following NFA positions, sorting them, and either reusing an existing state from a binary tree or allocating a new one.

`fol1` advances one regex node through alternation, begin/end anchors, byte classes, and optimized case tables, setting the global match flag when a terminal end state is reached.

`re2class` converts character classes into rune ranges, merges overlaps, handles negation, and lowers Unicode/UTF-8 rune ranges into byte-oriented regex fragments using `rclass`.

The design lazily builds DFA transitions during search, trading startup cost for incremental state construction.
