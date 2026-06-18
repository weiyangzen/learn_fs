# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont1.h

Defines Type 1 and Type 2 font internal data structures and callbacks.

Key definitions:
- `zone_table`, `float_array`, and `stem_table` macros define compact hint-parameter arrays.
- `gs_type1_data_procs_t` provides callbacks for glyph data, local/global subr data, seac data, and OtherSubrs push/pop stack interaction.
- `gs_type1_data` stores charstring interpreter callback, procedure data, parent Type 9 font, encryption length, Type 2 subr biases/random seed/default width/nominal width, and Type 1 hinting parameters.
- Hinting fields include Blue values, family zones, OtherBlues, StdHW/StdVW, StemSnapH/V, ForceBold, LanguageGroup, and WeightVector.
- `gs_font_type1` extends `gs_font_base_common` with `gs_type1_data`.
- Declares GC metadata for Type 1 fonts.

Key declarations:
- `gs_type1_glyph_info`
- `gs_type1_piece_codes`

Dependencies:
- Includes `gstype1.h` for the charstring interpreter proc and `gxfixed.h` for fixed widths.

Research notes:
- Type 1 and CFF Type 2 share this data structure because their runtime state is similar enough.
- `gs_type1_piece_codes` exists mainly for font copying of `seac` composite glyphs.
