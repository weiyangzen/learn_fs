# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfinp.c

Purpose: byte-order input helpers for `ttfReader`.

Key contents:
- Implements `ttfReader__Byte`, `ttfReader__SignedByte`, `ttfReader__Short`, `ttfReader__UShort`, `ttfReader__UInt`, and `ttfReader__Int`.
- Reads big-endian TrueType values from the abstract reader callback interface.

Dependencies: `ttmisc.h`, `ttfoutl.h`, `ttfsfnt.h`, `ttfinp.h`.

Integration notes: used by `ttfmain.c` to parse sfnt directories, metrics, glyph flags, coordinates, and instruction lengths.

Risks: functions assume `Read` succeeds; callers must check `r->Error(r)` separately.
