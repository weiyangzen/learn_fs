# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/merge.c

Merges multiple Plan 9 bitmap/subfont files by choosing the first available glyph for each character index.

Key functions:
- `main` reads all input fonts, validates compatible height/ascent, allocates merged bitmap and `Fontchar` array, calls `choose`, writes bitmap/subfont output.
- `snarf` reads one bitmap and subfont file into memory.
- `choose` iterates character slots, finds the first source font with nonempty glyph width, copies metrics and bitmap data into the merged output.

Notable issues:
- Compatibility checks compare against `ft[1]` rather than `ft[0]` in conditions, likely a bug for `nf > 1`.
- Contains a debugging display line: `bitblt(&screen,...); bflush(); sleep(5000);` before subfont allocation.
- Bitmap copy in `choose` uses `Pt(0, lastx)` and `Rect(0, info[n].x, ht, info[n+1].x)`, reflecting old libg coordinate conventions but worth reviewing if ported.
