# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/p9bitpost/pslib.h

Minimal interface for `p9bitpost` PostScript output library.

Key responsibilities:
- Declares `psinit()`, `image2psfile()`, and `psopt()`.
- Declares external paper dimensions.

Usage:
- Included by both the frontend and implementation.
