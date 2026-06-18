# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/fapi_ft.c

## Scope

Ghostscript FAPI plugin that renders fonts through FreeType.

## Key Behavior

- Defines `FF_server`, `FF_face`, and FreeType incremental-interface state for Ghostscript-supplied glyph data.
- Opens fonts from filesystem paths or from Ghostscript-serialized in-memory Type 1, Type 2, and TrueType data.
- Uses FreeType incremental callbacks to request glyph data and optionally override glyph metrics.
- Decomposes Ghostscript transforms into FreeType size and transform components for hinting and rendering.
- Provides FAPI callbacks for decoding ID, font bbox, glyph-name lookup, metrics replacement, character width, raster generation, outline generation, char-data release, and typeface release.
- Converts FreeType outlines into Ghostscript `FAPI_path` operations, including quadratic-to-cubic conversion.

## Dependencies

Uses Ghostscript FAPI/plugin headers, Type 1/Type 2 serialization helpers, and FreeType headers including incremental, glyph, outline, and trigonometry APIs.

## Risks And Invariants

- `char_data` may be cleared by Ghostscript glyph fetching hacks and is saved/restored around repeated loads.
- Incremental glyph buffers have one reusable buffer plus heap allocation for nested composite glyph requests.
- Raster and outline glyphs are stored on the server between paired metrics/data calls and must be released.
- FreeType errors are mapped coarsely to Ghostscript errors.
