# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ichar1.h

Declares Type 1/Type 2 character rendering support.

Exports:
- `charstring_execchar`: implementation entry for `.type1/2execchar`.
- `zchar1_glyph_outline`: glyph outline procedure.
- `zcharstring_outline`: build outline from a CharString for Type 1/2 and CIDFontType 0 usage.
- glyph info helpers.
- `z1_set_cache`: cache setup for rendered glyphs.

This header connects interpreter font operators to Type 1/2 charstring execution and glyph cache setup.
