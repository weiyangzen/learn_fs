# File Research: sources/virtualization/nbd/tests/parse/parser.c

## Purpose
Implements the test harness for `nbdtab` parser fixtures.

## Main Entry Points
- Stub callbacks `nbdtab_set_property()`, `nbdtab_set_flag()`, and `nbdtab_commit_line()` assert parser output against an expected `CLIENT`.
- `main()` selects the expected `CLIENT` based on the fixture filename, opens it as `yyin`, suppresses parser output via `yyout`, runs `yyparse()`, and checks whether a commit was seen for nonempty fixtures.

## Dependencies
Uses generated `nbdtab_parser.tab.h`, lexer/parser globals, and `nbdclt.h`.

## Risks and Notes
The harness only accepts property `bs` and flag `no_optgo`, matching the included fixtures. Additional parser features would need fixture and callback expansion.
