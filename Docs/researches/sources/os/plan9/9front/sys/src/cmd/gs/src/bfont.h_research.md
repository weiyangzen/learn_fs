# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/bfont.h

This header declares Ghostscript interpreter-internal routines and data used when building fonts.

Key responsibilities:
- Includes `ifont.h`.
- Declares `add_FID` for adding font identifiers to font dictionaries.
- Declares font make procedures `zdefault_make_font` and `zbase_make_font`.
- Exposes the global interpreter font directory `ifont_dir`.
- Defines `build_proc_refs`, holding `BuildChar` and `BuildGlyph` PostScript procedure refs.
- Defines `build_font_options_t` flags controlling font dictionary requirements and behavior:
  - optional encoding
  - ignored `UniqueID`
  - optional `CharStrings`
  - required `.notdef`
- Declares builders for primitive, simple, outline, FDArray, main, and sub-font construction.
- Declares helpers for font names, encoding glyphs, mapping glyphs to Unicode, and retrieving ToUnicode maps.

Dependencies and interfaces:
- Depends on Ghostscript interpreter types such as `i_ctx_t`, `ref`, `gs_font`, `gs_font_base`, `gs_font_dir`, `font_type`, and `gs_memory_type_ptr_t`.
- Serves as an internal interface between `zfont.c`, `zbfont.c`, and related font construction code.

Notable implementation details:
- It is declarations only; no executable logic.
- No filesystem or storage behavior is present.
- It is core Ghostscript interpreter font plumbing.

Research classification: internal Ghostscript font-building API header.
