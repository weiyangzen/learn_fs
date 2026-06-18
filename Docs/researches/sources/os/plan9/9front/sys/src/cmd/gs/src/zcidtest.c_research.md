# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcidtest.c

This file adds testing/debug operators for CIDFont and CMap facilities.

Key behavior:
- `.wrapfont` wraps TrueType, CID encrypted, CID user-defined, or CID TrueType fonts into Type 0 fonts.
- For Type 42 fonts, patches `BuildGlyph` to `%Type11BuildGlyph` and adjusts CIDMap behavior for PostScript BuildChar-backed Type 42 handling.
- `.writecmap` writes a CMap dictionary’s `CodeMap` structure to a writable file through `psf_write_cmap`.
- `.writefont9` writes a CIDFontType 0 / FontType 9 font to a writable file using `psf_write_cid0_font`.

Important dependencies:
- Uses font serialization support from `gdevpsf.h`.
- Uses `gxfont0c.h` Type 0 conversion helpers.
- Uses stream/file operators through `files.h` and `stream.h`.

Research notes:
- These operators are explicitly for testing facilities rather than normal language-level rendering.
