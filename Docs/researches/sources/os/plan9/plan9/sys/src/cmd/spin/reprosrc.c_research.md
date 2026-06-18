# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/reprosrc.c

This file reconstructs a readable Promela source representation from Spin’s internal parsed process list and sequence graph.

Main behavior:
- `repro_src()` starts from global `rdy` and calls `repro_proc()`.
- `repro_proc()` recursively walks to the end of the process list first, then prints each proctype in original-like order. It preserves deterministic proctype marker `D`, `provided` clauses, and the body.
- `repro_seq()` walks a `Sequence` from `frst` to `last`, printing labels, statements, branches, loops, and unless constructs.
- `repro_sub()` prints nested `d_step`, `atomic`, or non-atomic blocks.

Construct handling:
- Labels are recovered through `has_lab(e, 0)`.
- `UNLESS` is rendered as a normal block followed by an `unless` block.
- `DO` and `IF` nodes print `do`/`if`, each option with `::`, then `od`/`fi`.
- `ATOMIC`, `D_STEP`, and `NON_ATOMIC` nodes recurse into their nested sequence.
- Terminal/internal nodes `.`, `@`, and `BREAK` are suppressed.
- `C_CODE` and `C_EXPR` are printed through `plunk_inline()` and `plunk_expr()` respectively.
- Other statements use `comment(stdout, e->n, 0)` and append a semicolon.

State:
- Uses a single static `indent` counter and `doindent()` to print three spaces per indentation level.

Purpose in the larger Spin code:
- This is a pretty-printer/reproducer for the parsed AST/sequence representation, useful for diagnostics or source normalization.
- It depends on parser-created `Element`, `Sequence`, `SeqList`, label, and inline code structures defined and declared through `spin.h`.

Limitations:
- It is a reconstruction, not a token-preserving formatter.
- Comments, exact whitespace, and some syntactic sugar are not preserved.
