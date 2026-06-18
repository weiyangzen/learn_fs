# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfinp.c

TrueType font input helper routines.

Key behavior:
- Implements big-endian scalar reads through abstract `ttfReader` callbacks:
  - `ttfReader__Byte`
  - `ttfReader__SignedByte`
  - `ttfReader__Short`
  - `ttfReader__UShort`
  - `ttfReader__UInt`
  - `ttfReader__Int`
- Reads raw bytes through `r->Read`.
- Converts 2- and 4-byte values from TrueType big-endian order into host integers.

Dependencies and interactions:
- Includes `ttmisc.h`, `ttfoutl.h`, `ttfsfnt.h`, and `ttfinp.h`.
- Used heavily by `ttfmain.c` table and glyph parsing.

Research relevance:
- Small but central endian-safe input layer for SFNT/TrueType parsing.
