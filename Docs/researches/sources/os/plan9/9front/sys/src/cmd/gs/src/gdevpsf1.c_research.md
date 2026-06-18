# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsf1.c

## Purpose
Implements embedded Type 1 font writing for PostScript/PDF output.

## Key Behavior
- `psf_type1_glyph_data` adapts a Type 1 font’s glyph-data callback to the generic outline glyph interface.
- `psf_get_type1_glyphs` gathers selected Type 1 outline glyphs via the shared outline-glyph helper.
- Writes Type 1 font components:
  - font header,
  - `FontInfo`,
  - `FontName`,
  - `Encoding`,
  - `FontMatrix`,
  - `UniqueID`/`XUID`,
  - `FontBBox`,
  - main font dictionary values,
  - Private dictionary,
  - Subrs,
  - CharStrings,
  - final `definefont`.
- Supports subset-aware Encoding/CharStrings emission.
- Handles Type 1 eexec wrapping:
  - optional eexec encryption,
  - optional ASCIIHex encoding,
  - optional 512-zero padding or mark handling,
  - returns three length values for embedding contexts.
- Supports forcing encrypted CharStrings when source `lenIV < 0` but output requires a `lenIV`.
- Writes all Subrs even for subsets, with an in-code note that this may be improved later.

## Dependencies
Uses Ghostscript Type 1 font internals, glyph data APIs, stream filters, eexec/ASCIIHex encoding streams, parameter printer support, and the font-writing declarations from `gdevpsf.h`.

## Research Notes
This file owns classic Type 1 program serialization. Other font formats declared in `gdevpsf.h` are implemented in sibling files outside this grouped work item.
