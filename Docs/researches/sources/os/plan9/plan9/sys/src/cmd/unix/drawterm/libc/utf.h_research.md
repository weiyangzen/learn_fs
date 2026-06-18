# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utf.h

This header defines Plan 9 UTF/Rune types, constants, and API declarations.

Key contents:
- Defines `Rune` as unsigned int.
- Defines `UTFmax`, `Runesync`, `Runeself`, `Runeerror`, `Runemax`, and `Runemask`.
- Declares UTF conversion/search functions, rune-string functions, and rune classification/case functions.

Important details:
- Shared public header for the bundled UTF/rune implementation.
