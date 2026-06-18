# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxftype.h

## Purpose
Defines Ghostscript font type identifiers and bitmap font behavior values.

## Font Types
`font_type` values mirror PostScript `FontType` values:
- composite Type 0,
- Type 1 encrypted,
- Type 2 encrypted,
- user-defined,
- disk-based,
- CIDFontType 0,
- CIDFontType 1,
- CIDFontType 2,
- Chameleon,
- CID bitmap,
- TrueType Type 42.

## Bitmap Behavior
`fbit_type` values mirror `ExactSize`, `InBetweenSize`, and `TransformedChar` dictionary entries:
- use outlines,
- use bitmaps,
- transform bitmaps.

## Integration
Included by `gxfont.h` and indirectly used by all font implementation and font-copying paths for type dispatch.
