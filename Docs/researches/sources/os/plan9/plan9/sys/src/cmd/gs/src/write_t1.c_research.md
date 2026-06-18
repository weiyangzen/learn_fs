# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t1.c

Serializes a Type 1 font as textual PostScript for FreeType via the FAPI FreeType bridge.

Key points:
- Public function is `FF_serialize_type1_font`.
- Writes a `%!PS-AdobeFont-1` leading comment, a small main dictionary, and an encrypted Private dictionary.
- Main dictionary writes `/FontType 1`, `/FontMatrix`, `/Encoding StandardEncoding`, `/FontBBox`, then enters `eexec`.
- Private dictionary enables `WRF_output` encryption, writes four dummy bytes, then writes Type 1 private entries such as `MinFeature`, `password`, `lenIV -1`, `BlueFuzz`, `BlueScale`, `BlueShift`, blues arrays, `ForceBold`, `StdHW`, `StdVW`, `StemSnapH`, `StemSnapV`, and `/Subrs`.
- Reads font features through `FAPI_font` callbacks: `get_word`, `get_long`, `get_float`, and `get_subr`.
- Converts fixed or scaled values back to font units using divisors, commonly `16`.
- Handles short buffers by relying on `WRF_output` total-count semantics.

Dependencies and interactions:
- Includes `wrfont.h`, `write_t1.h`, and `<assert.h>`.
- Comments note the PostScript is non-standard because `/CharStrings` and `/PaintType` are omitted; FreeType gets glyph data through its incremental interface.

Research relevance:
- Key bridge between Ghostscript FAPI font data and FreeType Type 1 ingestion.
