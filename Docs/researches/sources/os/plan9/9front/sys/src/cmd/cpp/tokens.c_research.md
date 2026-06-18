# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/tokens.c

Token-row storage, copying, insertion, whitespace normalization, output buffering, and debug printing for cpp.

Important behavior:
- `maketokenrow()`/`growtokenrow()` manage dynamic token arrays.
- `insertrow()` replaces tokens at the current cursor and normalizes whitespace on both sides.
- `makespace()` prevents accidental token merging after macro expansion.
- `normtokenrow()` deep-copies token text and canonicalizes leading whitespace availability.
- `puttokens()` coalesces contiguous token text into a buffered writer unless dependency mode suppresses output.
- `setempty()` reduces a row to a newline token for skipped/control lines.
