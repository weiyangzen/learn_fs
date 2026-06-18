# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t1.h

Header for Type 1 font serialization through the FAPI FreeType bridge.

Key points:
- Includes `ifapi.h`.
- Declares `FF_serialize_type1_font(FAPI_font*, unsigned char*, long)`.
- Documents that the serializer emits PostScript code suitable for passing to FreeType via FAPI.

Dependencies and interactions:
- Implemented by `write_t1.c`.
- Used by FAPI FreeType integration code that needs to synthesize a Type 1 wrapper.

Research relevance:
- Small API boundary for Type 1 serialization in the Ghostscript font bridge.
