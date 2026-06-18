# File Research: sources/os/plan9/plan9/sys/src/cmd/strings.c

This file implements the Plan 9 `strings` utility.

Key behavior:
- Reads stdin or named files with `Biobuf`.
- Extracts runs of printable runes, default minimum length 6, configurable with `-m`.
- Prints byte offset and string content.
- Truncates very long runs to `BUFSIZE-1` runes and marks them with `...`.

Important details:
- Printable runes are ASCII space through `~` plus values above `0xA0`, excluding `Runeerror`.
- Uses `Bgetrune`, so offsets are tracked with `Boffset` over rune-decoded input.

Filesystem relevance:
- Indirect: file-inspection utility for arbitrary files/binaries.
