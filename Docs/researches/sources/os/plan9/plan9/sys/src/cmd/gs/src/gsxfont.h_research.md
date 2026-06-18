# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsxfont.h

Purpose: Defines opaque external-font client types for Ghostscript.

Key definitions:
- `gx_xglyph` is an opaque external glyph identifier.
- `gx_no_xglyph` is the all-bits-set sentinel.
- Forward declarations for `gx_xfont_procs` and `gx_xfont`.

Behavior:
- Keeps external font implementation details opaque to core users.
- Used by character cache code to store and render platform/external font glyphs.

Dependencies:
- Requires `ulong`.

Notable risks:
- None local; this is a small type boundary header.
