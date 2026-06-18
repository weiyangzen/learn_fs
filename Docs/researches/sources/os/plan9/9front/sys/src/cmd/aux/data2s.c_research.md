# File Research: sources/os/plan9/9front/sys/src/cmd/aux/data2s.c

Role: Converts stdin bytes into Plan 9 assembler `DATA` directives.

Behavior:
- Usage: `data2s name`.
- Emits a macro `D(o,s)` for 8-byte chunks, one `DATA namecode+offset(SB)/8, $string` per chunk.
- Escapes printable characters, quotes, backslashes, and non-printable bytes carefully for assembler string literals.
- Pads the final chunk with `\z`.
- Emits `GLOBL namecode` sized to padded length and `GLOBL namelen` plus `DATA namelen` storing original byte length.

Use case:
- Embedding arbitrary binary data into assembly objects as named code/data symbols.
