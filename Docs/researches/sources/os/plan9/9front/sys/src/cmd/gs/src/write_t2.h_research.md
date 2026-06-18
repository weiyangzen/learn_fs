# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t2.h

Header for Type 2/CFF font serialization through the FAPI FreeType bridge.

Key points:
- Includes `ifapi.h`.
- Declares `FF_serialize_type2_font(FAPI_font*, unsigned char*, long)`.
- Documents that the output can be passed to FreeType via FAPI.

Dependencies and interactions:
- Implemented by `write_t2.c`.
- Used by FreeType bridge code needing a CFF wrapper around Ghostscript font data.

Research relevance:
- Small API boundary for Type 2/CFF serialization in the Ghostscript font bridge.
