# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t2.h

Header for Type 2/CFF font serialization.

Key points:
- Includes `ifapi.h`.
- Declares `long FF_serialize_type2_font(FAPI_font*, unsigned char*, long)`.
- The function writes binary Type 2/CFF font data and returns total required length.

Dependencies and interactions:
- Implemented by `write_t2.c`.
- Used by the FAPI FreeType bridge.

Research relevance:
- Public FAPI bridge entry point for Type 2/CFF serialization.
