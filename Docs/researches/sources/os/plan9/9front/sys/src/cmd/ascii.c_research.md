# File Research: sources/os/plan9/9front/sys/src/cmd/ascii.c

ASCII/Latin-1 table and conversion utility.

Important behavior:
- With no operands, prints a table of characters in the selected base.
- Supports 128 or 256 character tables via `-8`.
- Supports hex, octal, decimal, or arbitrary base 2-36.
- Converts numeric text to character names, or input characters to numeric values.
- `-c`/`-t` switch character-output modes, with `-t` stripping to raw bytes.

The file is self-contained except for Plan 9 `bio` output helpers.
