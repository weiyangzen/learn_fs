# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/main.c

Command-line utility for producing bitmap/subfont data for selected Han character ranges.

Key points:
- Dispatch table supports four source modes: JIS, Big5, GB BDF, and GB quwei.
- Default sources include `../han/jis.bits`, `../han/jis16.bits`, `../han/big5.16.bits`, and `../han/cclib16fs.bdf`.
- Options:
  - `-f file` overrides source file.
  - `-r` treats requested values as raw source ordinals instead of Unicode Runes.
  - `-5` selects Big5.
  - `-s` selects 16-pixel glyph size instead of 24.
  - `-g` selects GB BDF.
  - `-q` selects GB quwei.
- Requires two positional arguments: inclusive `from` and `to`.
- Allocates `bits`, `chars`, and `found`; maps Unicode to source ordinals unless raw mode is set.
- Calls the selected bitmap reader, copies the bitmap into another allocated bitmap, builds a `Subfont` with `bf`, then writes both bitmap and subfont records to stdout.

Dependencies and interactions:
- Uses mappers and readers declared in `hdr.h`.
- Uses Plan 9 graphics APIs from `libg`.

Research relevance:
- Top-level generator tying charset maps and bitmap readers into Plan 9 font artifacts.
