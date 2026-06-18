# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/fontinfo.h

Automatically generated static font metric data; the file explicitly says not to edit it.

Defines:

- `szFontnames[32]`: PostScript/PDF base font names and variants such as Courier, Times, Helvetica, Palatino, Helvetica-Narrow, Bookman, AvantGarde, and NewCenturySchlbk.
- `ausCharacterWidths1[32][256]`: per-font width table, mainly used for Latin-1 style output.
- `ausCharacterWidths2[32][256]`: second per-font width table, used by the Unix font path for Latin-2 output.
- Disabled `aiUnderlineInfo[32][2]` under `#if 0`.

The width tables store 1000-em relative character widths indexed by byte value. `fonts_u.c` consumes these arrays to calculate rendered string widths for PS/PDF/draw style output, scaling by Antiword font size in half-points. The generated data is pure lookup state, with no control flow or allocation.
