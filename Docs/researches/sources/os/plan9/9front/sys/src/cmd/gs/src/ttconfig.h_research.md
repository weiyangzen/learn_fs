# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttconfig.h

TrueType configuration settings, modified from FreeType.

Key points:
- Includes `ttconf.h`.
- Comments state Ghostscript cut out the TrueType instruction interpreter, though this tree still contains interpreter-related interfaces/adapters.
- Leaves debugging and optional GCC 64-bit mode disabled by default.
- Defines `ALIGNMENT 8`.
- Enables `SECURE_COMPUTATIONS`.
- Enables `IGNORE_FILL_FLOW` so invalid contour orientation is still handled.
- Defines `Print(format, ap)` to `vfprintf(stderr, ...)` unless supplied externally.
- Computes FreeType byte-order constants from `WORDS_BIGENDIAN`.
- Enables `LOOSE_ACCESS` for big-endian non-bus-error systems.
- Leaves thread-safe/reentrant/static interpreter/static raster options undefined.
- Defines `TT_EXTEND_ENGINE`.

Dependencies and interactions:
- Used by FreeType-derived TrueType internals.
- Pulls architecture data through `ttconf.h`.

Research relevance:
- Controls numeric, raster, byte-order, threading, and extension behavior for embedded TrueType support.
