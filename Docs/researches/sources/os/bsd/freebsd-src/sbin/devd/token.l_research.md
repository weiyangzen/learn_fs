# File Research: sources/os/bsd/freebsd-src/sbin/devd/token.l

## Purpose
Lex scanner for `devd` configuration files.

## Main Elements
- Tracks `lineno`.
- Skips whitespace and `#`, `//`, and `/* ... */` comments.
- Emits block punctuation, semicolons, numbers, keywords, IDs, and quoted strings.
- Quoted strings support backslash-newline continuations with following whitespace skipped.
- `yyerror()` logs parse errors with line number and token text.

## Dependencies And Integration
Includes `devd.h` and generated `y.tab.h`; feeds tokens to `parse.y`.
