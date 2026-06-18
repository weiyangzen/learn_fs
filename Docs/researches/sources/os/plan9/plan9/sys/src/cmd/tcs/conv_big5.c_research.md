# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_big5.c

Big5 input/output converter for `tcs`.

Key functions:
- `big5proc` is a two-state decoder. Lead bytes are `>= 0xA1`; trail bytes map through ranges `0x40..0x7e` and `0xA1..0xFE` into `BIG5FONT` slots.
- `big5_in` reads bytes, feeds `big5proc`, flushes rune buffers to downstream converter with `OUT`.
- `big5_out` lazily builds `tab[rune] = big5_ordinal`, emits ASCII directly, and emits two-byte Big5 for mapped non-ASCII runes.

Error behavior:
- Bad font/glyph or unknown ordinal increments `nerrors`, optionally prints diagnostics under `squawk`, emits `BADMAP`/`BYTEBADMAP` unless `clean` is set.

Dependencies:
- `hdr.h`, `conv.h`, `big5.h`, global `tabbig5`.
