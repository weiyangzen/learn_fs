# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/wrfont.c

Support routines for serializing fonts as PostScript-like byte streams for the FAPI FreeType bridge.

Key points:
- Implements `WRF_init`, `WRF_wbyte`, `WRF_wtext`, `WRF_wstring`, `WRF_wfloat`, and `WRF_wint`.
- Maintains output pointer, byte limit, total byte count, optional encryption flag, and encryption key.
- `WRF_wbyte` writes only if within buffer limit but always increments total count, allowing callers to compute required size even with a short buffer.
- When encryption is enabled, applies Type 1 eexec-style encryption using key `55665`, factor `52845`, and offset `22719`.
- Formats floats and integers with `sprintf`.

Dependencies and interactions:
- Used by `write_t1.c` and `write_t2.c`.
- Struct and prototypes are in `wrfont.h`.

Research relevance:
- Shared bounded-output and encryption primitive for FAPI font serialization.
