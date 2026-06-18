# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/defont.c

Embeds the default Plan 9 bitmap font data for drawterm. The large `defontdata[]` array contains an uncompressed `lucm/latin1.9` font image plus packed font metrics.

Key data/functions:
- `defontdata[]`: byte representation of the default font image and fontchar records.
- `sizeofdefont`: size of embedded font data.
- `_unpackinfo`: converts packed 6-byte fontchar records into `Fontchar` structures.

Important behavior:
- This file is mostly static data; runtime interpretation is performed by libmemdraw’s default-font loader.
- `_unpackinfo` decodes `x`, `top`, `bottom`, `left`, and `width` for `n+1` entries, preserving the Plan 9 subfont convention.
