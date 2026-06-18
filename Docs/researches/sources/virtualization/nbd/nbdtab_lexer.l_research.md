# File Research: sources/virtualization/nbd/nbdtab_lexer.l

## Purpose
Defines the flex lexer for `nbdtab` configuration lines.

## Main Rules
- Includes generated `nbdtab_parser.tab.h`.
- Ignores comment lines starting with `#`.
- Returns `SPACE` tokens for spaces/tabs.
- Returns `STRING` tokens for runs excluding whitespace, comma, and equals.
- Returns literal single-character tokens for other characters, including newline.

## Dependencies
Uses `strdup()` to allocate token text into `yylval`. Tokens are consumed by `nbdtab_parser.y`.

## Risks and Notes
Allocated token strings are passed to parser actions without local freeing in this file. The grammar is intentionally small and line-oriented.
