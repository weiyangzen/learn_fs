# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/data2s.c

This file converts stdin bytes into Plan 9 assembler `DATA`/`GLOBL` directives.

Key behavior:
- Emits eight-byte string chunks as `DATA namecode+offset(SB)/8`.
- Escapes nonzero bytes as octal and zero bytes as `\z`.
- Pads the generated data to an eight-byte boundary.
- Emits globals for the data and a separate `namelen` length word.

Important details:
- Takes exactly one symbol-name prefix argument.
- Original unpadded byte length is preserved in `namelen`.

Filesystem relevance:
- Indirect: build utility for embedding binary file data into assembly.
