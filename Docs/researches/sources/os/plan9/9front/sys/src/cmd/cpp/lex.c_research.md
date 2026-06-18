# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/lex.c

Lexer for cpp. It encodes a compact finite-state machine and expands it into a `bigfsm[256][MAXSTATE]` table for tokenization speed.

Important behavior:
- Recognizes C preprocessing tokens: names, numbers, strings, char constants, comments, whitespace, operators, newlines, and EOF.
- Supports UTF byte sequences as identifier characters.
- Handles backslash-newline line folding, including ignored carriage returns before newline.
- Converts comments to whitespace while tracking line increments.
- `setsource()` loads an entire file or string into memory and appends EOFC sentinels.
- `gettokens()` fills a token row through newline or END and reports whether possible macro names were seen.
