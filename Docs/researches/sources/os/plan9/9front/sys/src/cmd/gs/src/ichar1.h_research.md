# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ichar1.h

Declares Type 1 / Type 2 character rendering interfaces.

Key points:
- Forward-declares `gs_font_type1`.
- Declares `charstring_execchar`, the implementation behind `.type1execchar` / `.type2execchar` style operators.
- Declares glyph-outline procedure for Type 1/2 fonts.
- Declares `zcharstring_outline` for extracting outlines from CharString data, including CIDFontType 0 use.
- Declares glyph info helpers, including a generic WMode-aware variant.
- Declares `z1_set_cache` for Type 1 glyph cache setup.

Research notes:
- This header connects interpreter font operators to Type 1/Type 2 charstring interpretation and cache setup.
