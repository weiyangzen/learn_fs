# File Research: sources/os/plan9/9front/sys/src/cmd/spin/reprosrc.c

## Purpose

`reprosrc.c` provides two related source-output utilities for Spin:

- AST-based reproduction of parsed Promela process bodies (`repro_src()`);
- token-stream pretty-printing from the lexer (`pretty_print()`).

It prints Promela-like source to stdout, preserving control structure and readable indentation rather than reproducing original whitespace exactly.

## AST Source Reproduction

`repro_src()` calls `repro_proc()` over the ready process list `rdy`, recursively printing later processes first. `repro_proc()` emits deterministic proctype prefix `D` when applicable, the proctype name, an optional `provided` clause, and the body.

`repro_seq()` walks a `Sequence` from first element to last. It prints labels from `has_lab()`, handles `unless` by printing normal and escape blocks, handles `do`/`if` options with `::`, descends into sub-sequences, and prints ordinary statements through `comment()`. It skips internal placeholders such as `.`, `@`, and `BREAK`. `repro_sub()` handles `d_step`, `atomic`, and `non_atomic` blocks.

For embedded C, `repro_seq()` prints `c_code` through `plunk_inline()` and condition C expressions through `plunk_expr()` in `c_expr { ... } ->` form.

## Lexer Pretty Printer

`pretty_print()` sets global `pp_mode`, reads tokens from `lex()` until EOF, and builds one printable line at a time in `buf`. It uses `blip()` to append token text and `purge()` to flush lines with indentation.

`blip()` maps raw characters and parser token constants to Promela text. It covers temporal operators, boolean/arithmetic operators, channel send/receive variants, declarations, embedded C constructs, process/claim/init syntax, labels, types, mtype/name/string tokens, priorities, `provided`, `unless`, and other Spin tokens. It uses `yylval` to print token-associated symbol names, constants, and types.

`purge()` prints the current buffer if non-empty, with special indentation for option separators beginning with `::`, then resets declaration/C-code state flags. `doindent()` prints three spaces per indent level.

## Formatting State

The pretty printer tracks:

- `indent`, the current indentation depth;
- `in_decl`, incremented around declarations and channel type syntax to influence line breaks;
- `in_c_decl` and `in_c_code`, set by C-specific tokens;
- `pp_mode`, an exported flag indicating lexer pretty-print mode.

`pretty_print()` inserts spaces between tokens unless they are punctuation or operator combinations where adjacent output is expected. It starts new lines for declarations, `c_decl`/`c_state`/`c_track`, option separators, `do`, `if`, and top-level type declarations. It adjusts indentation on `{`, `}`, `do`/`od`, and `if`/`fi`, and prints preprocessor tokens at indentation zero.

## Notable Risks and Behaviors

- AST reproduction omits some internal nodes and reconstructs structured source from Spin's normalized internal form, not the original text.
- The proctype printer currently emits `proctype name()` and does not reproduce original formal parameter lists in this function.
- `blip()` appends into a 1024-byte buffer without local bounds checks beyond a few assertions for preprocessor/name copies.
- Embedded C output delegates to `plunk_inline()` and `plunk_expr()`, so behavior depends on stored C fragments elsewhere.
