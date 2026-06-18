# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/wrfont.h

Header for shared font serialization output helper.

Key points:
- Includes `stdpre.h`.
- Defines `WRF_output` with current buffer pointer, buffer limit, total byte count, encryption flag, and encryption key.
- Declares byte/text/string/float/integer writer functions and initializer.

Dependencies and interactions:
- Used by Type 1 and Type 2 serializer implementations.
- Depends on Ghostscript’s `bool` definition from `stdpre.h`.

Research relevance:
- Public local contract for the small font writer utility used by FAPI FreeType bridge code.
