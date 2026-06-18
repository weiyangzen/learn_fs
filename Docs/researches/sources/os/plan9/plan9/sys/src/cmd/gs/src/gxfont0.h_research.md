# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont0.h

## Purpose
Defines Ghostscript Type 0 composite font data and procedure declarations.

## Mapping Types
Defines `fmap_type` values matching PostScript `FMapType` dictionary values:
- `fmap_8_8`
- `fmap_escape`
- `fmap_1_7`
- `fmap_9_7`
- `fmap_SubsVector`
- `fmap_double_escape`
- `fmap_shift`
- `fmap_CMap`

## Main Type
`gs_type0_data` stores:
- mapping mode and escape/shift bytes,
- `SubsVector` metadata,
- `Encoding`,
- `FDepVector`,
- optional `CMap`.

## Font Type
`gs_font_type0` embeds `gs_font_common` plus `gs_type0_data`.

## Declared Procedures
- `gs_type0_define_font`
- `gs_type0_make_font`
- `gs_type0_init_fstack`
- `gs_type0_next_char_glyph`

## Integration
Used for composite font dispatch and CID-wrapped fonts. It supplies the structures consumed by `gxfont0c.h` wrapper constructors.
