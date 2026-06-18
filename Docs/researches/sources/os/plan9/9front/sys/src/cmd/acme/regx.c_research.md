# File Research: sources/os/plan9/9front/sys/src/cmd/acme/regx.c

This file implements Acme's regular expression compiler and executor.

Key responsibilities:
- Defines regex VM `Inst` instructions and NFA thread-list `Ilist`.
- `rxinit()` initializes the regex compile channel and last-regexp buffer.
- `rxcompile()` compiles a rune regex into forward and backward programs, caching the last regex.
- `realcompile()` parses regex tokens into VM instructions using operator/operand stacks.
- Supports literals, `.`, `^`, `$`, grouping, alternation, concatenation, `*`, `+`, `?`, character classes, negated classes, and submatch ranges.
- Character class support: `nextrec()`, `bldcclass()`, `classmatch()`.
- VM support: `newinst()`, `operand()`, `operator()`, `evaluntil()`, `optimize()`.
- `rxexecute()` runs forward search over `Text` or rune string input.
- `rxbexecute()` runs backward search over `Text`.
- `newmatch()` and `bnewmatch()` select best forward/backward match ranges.
- `rxnull()` reports no compiled regex.

Important dependencies:
- Reads text through `textreadc()` when searching buffers.
- Reports compile/runtime warnings via `warning()` and uses a worker thread for compilation.

Filesystem/storage relevance:
- Regexes drive Acme addresses, edit commands, and search. Those operations select and mutate file-backed buffers and external file-server ranges.

Notes:
- Program size is fixed at `NPROG` instructions and active thread list at `NLIST`.
- Backward compilation reverses concatenation order, enabling reverse search rather than scanning all forward matches.
