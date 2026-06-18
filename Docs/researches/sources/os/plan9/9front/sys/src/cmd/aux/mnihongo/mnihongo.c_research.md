# File Research: sources/os/plan9/9front/sys/src/cmd/aux/mnihongo/mnihongo.c

`mnihongo` filters troff device-independent output, replacing characters from a Japanese font position with PostScript bitmap masks generated from Plan 9 bitmap fonts. It preserves most troff output commands while tracking horizontal and vertical positions.

It loads `/lib/font/bit/pelm/unicode.9x24.font`, opens subfonts lazily by rune range, renders a rune into a `Memimage`, unloads 1-bit rows into hexadecimal image data, and emits `x X PS ... imagemask` commands at the current troff position.

The parser handles troff motions, font changes, device-control `x` records, drawing records, comments, page/newline commands, and the compact `nnc` motion+character form. It identifies the Japanese font by seeing `x f <slot> Jp...` controls.

Caveats: the code assumes the pelm font layout and has small fixed buffers for strings and row data; failures in font parsing or subfont loading are fatal.
