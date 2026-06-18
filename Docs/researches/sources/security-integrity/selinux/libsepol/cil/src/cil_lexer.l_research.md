# sources/security-integrity/selinux/libsepol/cil/src/cil_lexer.l

## Purpose
`cil_lexer.l` is the Flex scanner for CIL syntax. It tokenizes the CIL input stream into parentheses, symbols, quoted strings, comments, high-level-language line markers, newlines, EOF, and unknown characters.

## Important APIs, Types, And Functions
The generated scanner is wrapped by `cil_lexer_setup`, `cil_lexer_destroy`, and `cil_lexer_next`. Patterns define digits, letters, special symbol characters, whitespace, newlines, quoted strings, `;;*` high-level line markers, and `;` comments. The scanner uses Flex options `nounput`, `noinput`, `noyywrap`, and prefix `cil_yy`.

## Control Flow
`cil_lexer_setup` scans a caller-provided buffer and resets line number to 1. Each scanner action returns one token type or skips whitespace. Newlines increment the global line counter. `cil_lexer_next` calls `yylex`, copies the current token type/value/line into the caller's token, and returns `SEPOL_OK`.

## State And Persistence Behavior
The file uses scanner-global `value` and `line`. It does not allocate token strings; `yytext` points into scanner-managed buffer content. Parser code modifies quoted string buffers in place to strip quotes before interning.

## Dependencies And Integration Points
It includes `cil_internal.h`, `cil_lexer.h`, `cil_log.h`, and `cil_mem.h`, and reports setup errors through `cil_log`. `cil_parser.c` supplies the buffer from the public CIL loader.

## Risks And Edge Cases
The grammar intentionally recognizes comments as a single `;` token and leaves parser code to consume until newline. Quoted strings cannot contain quotes, newlines, or NUL. `value` is not reset for whitespace/newline/EOF paths, but token type controls use. The high-level line marker pattern is anchored and must remain consistent with parser expectations.

## Test Signals
Unit tests should verify token order, line counters, comment consumption by the parser, quoted string stripping, unknown-token diagnostics, and setup failure behavior for malformed scan buffers.
