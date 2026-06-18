# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/font/merge.c

Merges multiple Plan 9 subfont files by selecting the first available glyph for each character.

Key points:
- Loads up to 1024 bitmap/subfont pairs into global `ft`.
- `snarf` opens each file, reads its bitmap with `rdbitmapfile`, copies it into owned storage, then reads the associated subfont with `rdsubfontfile`.
- `main` computes the largest character count and checks height/ascent compatibility before allocating an output bitmap and `Fontchar` array.
- `choose` iterates all character indices and source fonts, selecting the first font whose glyph has nonzero width, copying metrics and bitmap bits into the merged output.
- Writes a bitmap file followed by a subfont file to stdout.
- Contains an apparent compatibility-check typo: inside the loop it compares each font against `ft[1].sf->height/ascent` while printing expected values from `ft[0]`; this likely should compare against `ft[0]`.
- Contains leftover interactive/debug code that blits the merged bitmap to `screen`, flushes, and sleeps for five seconds before writing the subfont.
- `choose` calls `bitblt(b, Pt(0, lastx), ...)`; given the output bitmap dimensions, this coordinate order looks suspicious and may reflect old libg coordinate conventions or a bug.

Dependencies and interactions:
- Built separately by `font/mkfile` as `merge`.
- Intended to combine generated font shards, for example `/lib/font/bit/gb/*.7000.24`.

Research relevance:
- Utility for composing generated subfonts, with notable old/debug code paths worth care if reused.
