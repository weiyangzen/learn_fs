# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifont2.h

Declares Type 2-specific font parameter parsing.

Key points:
- Defines Type 2 default `lenIV` as `-1`.
- Declares `type2_font_params`, which extracts Type 2 parameters beyond the common Type 1/Type 2 CharString parameters.

Dependencies and interactions:
- Requires `charstring_font_refs_t` and `gs_type1_data`, so it works with `ifont1.h` utilities.
- Used for Type 2 fonts and FontType 2 FDArray entries in CIDFontType 0 fonts.

Research relevance:
- Small specialization point for Type 2/CFF-style font handling.
