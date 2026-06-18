# sources/storage-engines/sqlite/tool/stripccomments.c

## Purpose
`stripccomments.c` filters stdin to stdout while removing C (`/* ... */`) and C++ (`// ...`) comments. It optionally preserves the first N comments via repeated `--keep-first`/`-k`, typically for license headers.

## Important APIs, types, and functions
Global `App` stores input/output streams, return code, and keep count. `do_it_all()` implements a character-level state machine with states `S_NONE`, `S_SLASH1`, `S_CPP`, and `S_C`. It preserves string-like literals delimited by single quote, double quote, or backtick, treating backslash as an escape marker. `usage()` reports valid flags.

## Control flow
`main()` parses only `-k`/`--keep-first`, assigns stdin/stdout to `App`, and calls `do_it_all()`. The filter scans one character at a time, delaying output of `/` until it knows whether it begins a comment. When inside comments, it either suppresses output or passes through preserved comments. Newlines end `//` comments and update line/column counters.

## State and persistence behavior
The program is streaming and writes only stdout. It maintains parser state, previous character, line/column counters, and a `state3Col` workaround for a corner case involving `/*/`.

## Dependencies and integration points
It uses only standard C and is a source preprocessing helper for build or analysis pipelines that need comment-stripped input.

## Risks and edge cases
The tool assumes legal C-like code and is intentionally limited. It can strip comment-looking text inside heredocs or language-specific constructs. Regex handling is only a narrow workaround for slash-asterisk preceded by backslash. Unterminated string literals are reported as errors, but unterminated comments receive little special handling.

## Test signals
Tests should cover normal block and line comments, repeated `-k`, strings containing comment markers, backtick literals, escaped quotes, the documented `/*/` corner case, and unexpected EOF inside a string.
