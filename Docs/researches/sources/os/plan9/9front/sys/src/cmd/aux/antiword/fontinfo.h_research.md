# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fontinfo.h

This is an automatically generated font metrics header used by the Unix font backend.

Contents:
- `szFontnames[32]`: PostScript-compatible font names, including Courier, Times, Helvetica, Palatino, Helvetica-Narrow, Bookman, AvantGarde, and NewCenturySchlbk variants.
- `ausCharacterWidths1[32][256]`: 256-entry character width tables for each font, used for Latin-1 style width computation.
- `ausCharacterWidths2[32][256]`: parallel 256-entry width tables for Latin-2.
- Disabled `aiUnderlineInfo[32][2]` under `#if 0`, noted as unused until needed.

Important behavior:
- No functions are defined; this is static data included by `fonts_u.c`.
- Width values are in relative font units and are scaled by `lComputeStringWidth`.
- Many control-code slots are zero, while printable ranges and extended character positions carry per-font metrics.

Dependencies:
- Included directly by Unix font handling; array sizes are assumed by `fonts_u.c`.

Role in antiword:
- Enables deterministic text width calculation without querying a platform font system.
