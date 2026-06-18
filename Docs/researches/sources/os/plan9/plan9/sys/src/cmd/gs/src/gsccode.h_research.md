# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsccode.h

Defines Ghostscript character-code and glyph-code types and encoding indices.

Key contents:
- Defines `gs_char` as `ulong`, with `GS_NO_CHAR`/`gs_no_char`.
- Defines `gs_glyph` as `ulong`, with reserved numeric regions for:
  - no glyph / unknown glyph
  - global named glyphs
  - built-in encoding private glyphs
  - CIDs
  - glyph indices
- Defines boundaries:
  - `GS_NO_GLYPH`
  - `GS_MIN_CID_GLYPH`
  - `GS_MIN_GLYPH_INDEX`
  - `GS_GLYPH_TAG`
  - `GS_MAX_GLYPH`
- Defines `gs_glyph_mark_proc_t` for GC marking.
- Defines `gs_encoding_index_t` for 11 known encodings:
  - 7 real encodings: Standard, ISOLatin1, Symbol, Dingbats, WinAnsi, MacRoman, MacExpert
  - 4 pseudo/glyph-set encodings: MacGlyph, Adobe Latin Original, Adobe Latin Extended, CFF StandardStrings
- Defines `KNOWN_REAL_ENCODING_NAMES`.
- Defines `gs_glyph_space_t` for name/index/no-generation glyph selection.
- Defines `gs_glyph_name_proc_t`.

Important implementation notes:
- The header establishes the namespace contract used by `gscencs.[ch]` and generated encoding tables.
- Built-in encoding glyphs live below CID glyph values but in a private reserved range.
- Composite fonts require character codes to be at least 32 bits; this is why `gs_char` is not simply `byte`.
