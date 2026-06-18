# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcidtest.c

Implements internal/testing operators for CIDFont and CMap facilities.

Key behavior:
- `.wrapfont` wraps the current Type 42 or CID font into a Type 0 composite font. For Type 42 fonts, it patches `CIDMap` and `BuildGlyph` to suit PostScript-implemented BuildChar behavior.
- `.writecmap` serializes a CMap dictionary’s `CodeMap` to a writable file with `psf_write_cmap`.
- `.writefont9` serializes a CIDFontType 0 encrypted font using `psf_write_cid0_font`.

Dependencies and coupling:
- Uses font serialization support from `gdevpsf.h`.
- Intended as test/support functionality, not general user-facing PostScript behavior.
