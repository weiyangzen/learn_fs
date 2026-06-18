# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/bfont.h

This header declares internal Ghostscript interpreter routines and data used while building fonts from PostScript font dictionaries.

Key contents:
- Includes `ifont.h` and requires `gxfont.h` context.
- Declares `add_FID`, default/base font make procedures, and the global interpreter font directory `ifont_dir`.
- Defines `build_proc_refs`, carrying `BuildChar` and `BuildGlyph` procedure refs.
- Defines `build_font_options_t` flags controlling how font dictionary parameters are interpreted, such as optional encoding, ignored `UniqueID`, optional `CharStrings`, and required `.notdef`.
- Declares font construction helpers implemented in `zbfont.c`, including primitive/simple/outline/FDArray/sub-font builders.
- Declares font definition, font-name extraction/copying, glyph encoding, glyph-to-Unicode mapping, and ToUnicode map lookup helpers.

This is interpreter/font infrastructure only. It has no filesystem logic.
