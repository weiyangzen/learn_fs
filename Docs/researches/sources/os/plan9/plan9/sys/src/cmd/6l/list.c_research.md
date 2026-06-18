# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/list.c

This file implements formatted diagnostics and instruction listing for the amd64 linker. It installs formatters for registers, opcodes, operands, string constants, and `Prog` records.

`Pconv` prints instructions with line numbers and special formatting for `TEXT`, `DATA`, `INIT`, and `DYNT`. `Dconv` formats operands, including branch targets resolved through `pcond`, extern/static/auto/param symbols, constants, floating constants, string constants, and address constants. `Rconv` maps register numbers to names. `Sconv` escapes string constants.

`diag` reports linker errors in the context of the current text symbol and exits after too many errors. This makes object/link failures tied to the function being processed rather than only the raw object file.

Filesystem relevance is diagnostic: it helps debug failed OS/filesystem builds by rendering linker instructions, operands, and symbol contexts.
