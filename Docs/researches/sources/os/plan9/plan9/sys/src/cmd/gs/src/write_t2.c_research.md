# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t2.c

Serializes a Type 2/CFF font in binary format for FreeType via the FAPI FreeType bridge.

Key points:
- Public function is `FF_serialize_type2_font`.
- Writes CFF header, dummy name index, top/font dictionary index, empty string index, subrs index, charset, charstrings index, and private dictionary.
- Encodes Type 2 integers using compact CFF number forms and writes larger values with 4-byte big-endian encoding.
- Encodes Type 2 real numbers from `sprintf("%f")` into CFF nibble format.
- Top dictionary writes FontBBox, FontMatrix, Standard Encoding, placeholders for charset and CharStrings offsets, and placeholder size/offset for Private dictionary.
- Charset is minimal and currently reports one character, enough for FreeType incremental use.
- CharStrings index contains empty charstrings and exists mainly to communicate glyph count.
- Subrs index writes offsets and subroutine data from `FAPI_font->get_subr`.
- Private dictionary writes hinting/private features including blue zones, stem data, force-bold, default width, and nominal width.
- Extracts default/nominal widths directly from `gs_font_type1` via `a_fapi_font->client_font_data`.

Dependencies and interactions:
- Includes `wrfont.h`, `write_t2.h`, `ghost.h`, `gxfont.h`, and `gxfont1.h`.
- Relies on FAPI callbacks for font features and subroutines.
- Uses `fixed2float` for Type 1 font width fields.

Research relevance:
- Key bridge for converting Ghostscript/FAPI Type 1-like data to minimal CFF/Type 2 data that FreeType can consume incrementally.
