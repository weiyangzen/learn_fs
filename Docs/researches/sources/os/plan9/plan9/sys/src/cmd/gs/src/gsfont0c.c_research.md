# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont0c.c

## Role

Creates Type 0 composite font wrappers around CIDFonts and Type 42 fonts converted to CIDFontType 2.

## Main Data

Builds a single-entry `FDepVector`, one-entry dynamic `Encoding`, and either an identity CMap or a CMap derived from a TrueType cmap.

## Control Flow

`type0_from_cidfont_cmap` allocates a `gs_font_type0`, initializes FontMatrix, composite procs, name fields, `FMapType=fmap_CMap`, descendant vector, and CMap, then defines it in the font directory. `gs_font_type0_from_cidfont` creates an identity CMap and wraps a CIDFont. `gs_font_type0_from_type42` converts Type42 to CIDFontType2, optionally derives a CMap from the Type42 cmap, then wraps it.

## Dependencies

Uses CID font, CMap, Type42, and Type0 font internals.

## Notes

Error paths contain comments noting incomplete freeing of substructures.
