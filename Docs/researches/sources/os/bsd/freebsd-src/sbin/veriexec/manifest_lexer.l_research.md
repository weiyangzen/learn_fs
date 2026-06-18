# File Research: sources/os/bsd/freebsd-src/sbin/veriexec/manifest_lexer.l

## Purpose
Lex scanner for signed Veriexec manifest contents.

## Main Elements
- Tracks `lineno` and beginning-of-line state.
- Returns `PATH` for the first token on a line and `STRING` for subsequent tokens.
- Recognizes `=`, newline as `EOL`, whitespace, comments, and invalid characters.
- Supports version-gated `#>NUMBER` directives by treating the remainder of the line as a comment when parser version is too old.
- `manifest_open()` opens manifest content from an in-memory signed buffer via `fropen()`, resets lexer/parser state, and records the file name for diagnostics.
- `read_string_buf()` feeds bytes from the signed buffer to stdio.
- `yyerror()` reports `file: line: message at token`.

## Dependencies And Integration
Used by `manifest_parser.y`; receives verified manifest text from `veriexec.c`.

## Risk Notes
The lexer scans trusted-after-verification content from memory. Tokenization is simple and does not support quoted whitespace in fields.
