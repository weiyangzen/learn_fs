# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t2.c

Serializer for a minimal Type 2/CFF font wrapper for the FAPI FreeType bridge.

Key points:
- Public entry point is `FF_serialize_type2_font`.
- Writes a CFF header, dummy name index, top/font dictionary index, empty string index, subr index, charset, CharStrings index, and Private dictionary.
- Implements CFF integer and real-number encoders.
- Uses placeholder five-byte integer slots for charset, CharStrings, and Private dictionary offsets/lengths, then patches them when positions are known.
- Charset is intentionally minimal: currently one character, with `.notdef` assumptions.
- CharStrings index contains empty charstrings only to communicate glyph count to FreeType.
- Subr index serializes subroutines obtained from `FAPI_font->get_subr`.
- Private dictionary writes blue-zone, stem, force-bold, default width, and nominal width values.
- Reads `defaultWidthX` and `nominalWidthX` by casting `a_fapi_font->client_font_data` to `gs_font_type1*`.
- Like `wrfont`, returns total required byte count even if the caller buffer is too small.

Dependencies and interactions:
- Includes `wrfont.h`, `write_t2.h`, `ghost.h`, `gxfont.h`, `gxfont1.h`, and `<assert.h>`.
- Uses FAPI feature IDs and Ghostscript Type 1 font internals.

Research relevance:
- Minimal CFF wrapper generation for FreeType’s incremental font path. It is intentionally not a full CFF font serialization of all glyph data.
