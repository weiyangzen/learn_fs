# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsf1.c

## Purpose
Implements embedded Type 1 font serialization for PostScript/PDF output.

## Key Behavior
- `psf_type1_glyph_data` adapts Type 1 font glyph callbacks to the generic outline-glyph interface.
- `psf_get_type1_glyphs` gathers selected Type 1 outline glyphs via the shared outline-glyph helper.
- Writes Type 1 font program components:
  - `%!FontType1` header,
  - `FontInfo`,
  - `FontName`,
  - `Encoding`,
  - `FontMatrix`,
  - `UniqueID` / `XUID`,
  - `FontBBox`,
  - main font dictionary values,
  - Private dictionary,
  - Subrs,
  - CharStrings,
  - final `definefont`.
- Handles subset-aware `Encoding` and `CharStrings` emission using sorted subset lookup.
- Writes Private dictionary values through the parameter-printer path and emits Type 1 private arrays such as blue values and stem snap arrays.
- Writes all Subrs even for subsets, with an explicit note that this could be improved.
- Supports eexec wrapping, optional ASCIIHex output, optional 512-zero padding or mark handling, and reports three segment lengths for embedding contexts.
- If source `lenIV < 0` but output requires `lenIV`, encrypts CharStrings with `lenIV = 0`.

## Dependencies
Uses Type 1 font internals, glyph data callbacks, glyph enumeration helpers, PostScript string writing, parameter printer support, eexec and ASCIIHex stream filters, and declarations from `gdevpsf.h`.

## Research Notes
The implementation is serialization-focused and does not allocate/free font data itself beyond temporary glyph collection through shared helpers. Error handling is mostly return-code based, but several stream writes are not immediately checked for stream failure.
