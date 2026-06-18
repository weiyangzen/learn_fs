# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsxfont.h

Declares opaque external-font client types for Ghostscript.

Key definitions:
- `gx_xglyph` is an opaque external-font glyph identifier, represented as `ulong`.
- `gx_no_xglyph` is the all-ones sentinel for no external glyph.
- Forward-declares `gx_xfont_procs` and `gx_xfont` as opaque structures.

Research notes:
- This header intentionally does not expose external-font procedure layout; implementation consumers include deeper headers such as `gxxfont.h`.
