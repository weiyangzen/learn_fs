# File Research: sources/os/plan9/plan9/sys/src/cmd/sed.c

Plan 9 stream editor implementation.

Key behavior:
- Parses sed programs from `-e`, `-f`, or a positional script.
- Supports addresses by line number, `$`, regular expression, and last regular expression.
- Implements command compilation for append/change/insert, branch/test, delete, hold/get/exchange, next, print, quit, read, substitute, write, transliterate, labels, and grouped blocks.
- Executes commands over concatenated input streams with a pattern space and hold space.
- Uses Plan 9 rune regex APIs for Unicode-aware matching and substitution.

Important details:
- Program storage and buffers are fixed-size arrays.
- Labels are resolved after compilation by `dechain()`.
- Substitution supports `g`, `p`, `P`, and `w file`.
- Pending `a` and `r` commands are queued and emitted after the current cycle.
- `l` command escapes non-printing runes with `\xNNNN` style output.

Filesystem relevance:
- Direct file I/O for script files, input files, `r` command reads, and `w` command output files.
