# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t1.h

Header for Type 1 font serialization.

Key points:
- Includes `ifapi.h`.
- Declares `long FF_serialize_type1_font(FAPI_font*, unsigned char*, long)`.
- The function writes serialized Type 1 font data into a caller buffer and returns the full required length.

Dependencies and interactions:
- Implemented by `write_t1.c`.
- Used by the FAPI FreeType bridge.

Research relevance:
- Public FAPI bridge entry point for Type 1 serialization.
