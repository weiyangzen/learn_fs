# File Research: sources/os/plan9/9front/sys/src/cmd/sam/regexp.c

`regexp.c` implements sam's regular expression compiler and executor. It builds a compact NFA-like instruction program and supports forward and backward execution.

The parser recognizes literals, escaped characters, `.`, `^`, `$`, character classes and negated classes, grouping, alternation, concatenation, `*`, `+`, and `?`. It uses operand/operator stacks, records subexpression boundaries up to `NSUBEXP`, and builds both forward and backward programs.

`compile` caches the last compiled regex, frees character classes, compiles forward and backward versions, optimizes away `NOP` chains, and updates `lastregexp`.

`execute` runs the forward machine from a starting position to EOF or a bound, with wrapping search semantics for unbounded search, first-character optimization, thread-list deduplication, submatch range tracking, anchors, classes, and longest-leftmost match selection.

`bexecute` mirrors execution backward, using a backward-compiled program and reversed range selection. `newmatch` and `bnewmatch` choose the best match for forward and backward searches.

Errors reset `lastregexp` before propagating through sam's `error` path.
