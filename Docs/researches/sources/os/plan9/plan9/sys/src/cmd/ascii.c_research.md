# File Research: sources/os/plan9/plan9/sys/src/cmd/ascii.c

ASCII/Latin-1 table and converter utility.

Key points:
- Prints an ASCII table by default, 128 or 256 entries with `-8`.
- Supports numeric bases via `-x`, `-o`, `-d`, or `-b n`.
- Converts numeric input to named/text characters, or text input to numeric values depending on mode.
- `-n` forces numeric output from text; `-c`/`-t` selects character conversion, with `-t` stripping to raw bytes.

Dependencies:
- Uses Plan 9 `bio`.

Notable behavior:
- Base range is 2 through 36.
- Table strings include extended Latin-1 labels for bytes 0xa1 through 0xff.
