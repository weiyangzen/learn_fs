# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t1.c

Serializer for a minimal Type 1 PostScript font wrapper for the FAPI FreeType bridge.

Key points:
- Public entry point is `FF_serialize_type1_font`.
- Writes `%!PS-AdobeFont-1`, a main dictionary, and an eexec-encrypted Private dictionary.
- Main dictionary writes `/FontType 1`, `/FontMatrix`, `StandardEncoding`, and `/FontBBox`.
- Private dictionary writes `/MinFeature`, `/password`, `/lenIV -1`, blue-zone fields, stem fields, force-bold data, and subrs.
- Pulls font feature values from `FAPI_font` callbacks: `get_word`, `get_long`, `get_float`, and `get_subr`.
- Converts some values from 16-scaled values back to font units.
- `write_subrs` writes subroutines through `RD ... NP` records and supports buffer-short sizing behavior.
- The comment explicitly notes the output is non-standard: no `/Charstrings` and no `/PaintType`; glyphs are supplied to FreeType through incremental interface mechanisms.

Dependencies and interactions:
- Includes `wrfont.h`, `write_t1.h`, and `<assert.h>`.
- Relies on FAPI feature IDs from `ifapi.h`.

Research relevance:
- Important bridge code for feeding existing Ghostscript Type 1 font metadata into FreeType without constructing a complete standard Type 1 font file.
