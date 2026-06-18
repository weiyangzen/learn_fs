# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifont1.h

Declares shared utilities for Type 1, Type 2, and other CharString-based fonts.

Key points:
- Defines `charstring_font_refs_t` with refs to:
  - `Private`
  - `OtherSubrs`
  - `Subrs`
  - `GlobalSubrs`
  - `no_subrs`
- Defines Type 1 default `lenIV` as `4`.
- Declares:
  - `charstring_font_get_refs`
  - `charstring_font_params`
  - `charstring_font_init`
  - `build_charstring_font`

Dependencies and interactions:
- Used by Type 1/2/CIDFontType0 builders.
- Bridges PostScript font dictionaries/FDArray entries into `gs_type1_data` and `gs_font_type1`.

Research relevance:
- Shared parsing/build path for encrypted CharString font data and subroutine dictionaries.
