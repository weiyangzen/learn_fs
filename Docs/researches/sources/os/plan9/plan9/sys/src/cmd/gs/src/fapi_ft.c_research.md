# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/fapi_ft.c

Ghostscript Font API plug-in backed by FreeType.

Key points:
- Implements an `FAPI_server` named `FreeType`.
- Lazily initializes an `FT_Library`.
- Supports fonts loaded from disk paths via `FT_New_Face` and embedded fonts loaded from serialized in-memory Type 1, Type 2, or TrueType data.
- Uses FreeType’s incremental interface to ask Ghostscript callbacks for glyph data and replacement metrics.
- Converts FreeType errors to Ghostscript error codes.
- Handles font scaling by decomposing the Ghostscript matrix into size and rotation/shear components for FreeType hinting and transforms.
- Provides FAPI callbacks for:
  - scaled font acquisition
  - decoding ID (`Unicode`)
  - font bounding box
  - glyph-name lookup
  - metric replacement decisions
  - character width
  - raster metrics/raster retrieval
  - outline metrics/outline retrieval
  - char data and typeface release
- Converts FreeType quadratic outlines to cubic curves for Ghostscript path callbacks.
- Plugin lifecycle is exposed through `gs_fapi_ft_instantiate` and `gs_freetype_destroy`.

Dependencies and interactions:
- Includes Ghostscript FAPI headers and Type 1/Type 2 serialization helpers.
- Includes FreeType headers for face loading, incremental fonts, glyphs, outlines, and transforms.
- Stores `FF_face` in `FAPI_font.server_font_data`.

OS/filesystem relevance:
- Uses FreeType disk font loading when `font_file_path` is present.
- Otherwise primarily in-memory serialization and callback-driven glyph retrieval.
