# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/main.c

Main program for generating Plan 9 bitmap/subfont data for a range of Han characters.

CLI behavior:
- Usage: `fontgen [-s] from to`, with additional options `-f file`, `-r`, `-5`, `-g`, `-q`.
- `-s` selects 16px instead of default 24px.
- `-5` selects Big5, `-g` GB BDF, `-q` GB quwei, otherwise JIS.
- `-r` treats requested codes as raw glyph indices rather than mapping from runes.

Flow:
- Chooses source mapping and bitmap reader.
- Allocates `bits`, `chars`, and `found`.
- Maps runes to glyph indices unless raw mode.
- Reads glyph bitmaps, copies bitmap, builds subfont with `bf`, then writes bitmap and subfont to stdout.

Dependencies:
- Plan 9 graphics initialization via `binit`.
