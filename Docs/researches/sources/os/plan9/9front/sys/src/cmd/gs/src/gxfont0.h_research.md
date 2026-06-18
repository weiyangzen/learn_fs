# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont0.h

Defines Type 0 composite font data structures and procedures.

Key definitions:
- `fmap_type` enumerates Type 0 `FMapType` values: `8/8`, escape, `1/7`, `9/7`, SubsVector, double escape, shift, and CMap.
- `fmap_type_is_modal` identifies escape/double-escape/shift mapping modes.
- `gs_type0_data` stores mapping controls, SubsVector metadata, Encoding, FDepVector, and optional CMap.
- `gs_font_type0` extends `gs_font_common` with `gs_type0_data`.
- Declares GC structure metadata for Type 0 fonts.

Key declarations:
- `gs_type0_define_font`
- `gs_type0_make_font`
- `gs_type0_init_fstack`
- `gs_type0_next_char_glyph`

Dependencies:
- Forward-declares `gs_cmap_t`.
- Uses `gs_font_common` and font proc macros from `gxfont.h`.

Research notes:
- Type 0 fonts are dispatch/wrapper fonts that map input character codes into descendant fonts.
- This header provides the data layout consumed by composite-font show enumeration.
