# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sstring.c

String and hex-string stream filters plus shared hex decode utility.

Key behavior:
- `ASCIIHexEncode` emits uppercase hex, inserts newlines after 32 source bytes, and optionally appends `>`.
- `ASCIIHexDecode` uses `s_hex_process`, handles odd final hex digits by padding the low nibble, scans for `>`, and returns `EOFC` at EOD.
- `PSStringEncode` escapes PostScript literal-string special characters, control characters, and non-ASCII bytes, appending `)` on final input.
- `PSStringDecode` parses literal strings, escape sequences, octal escapes, line continuations, nested parentheses, CR/LF normalization, and scanner-specific `from_string` mode.
- `s_hex_process` is a reusable hex scanner supporting whitespace-ignore, leading-whitespace-only, and garbage-ignore modes while preserving odd digit state across calls.

Notable dependencies:
- Scanner character table from `scanchar.h`.
- Stream state definitions from `sstring.h`.

Research notes:
- The decoder relies on the Ghostscript cursor convention and backs up input when it needs more bytes to complete an escape.
- `PSStringDecode` treats `)` at depth zero as `EOFC`, matching PostScript literal string termination.
