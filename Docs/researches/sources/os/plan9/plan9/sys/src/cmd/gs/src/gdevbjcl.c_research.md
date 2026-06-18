# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbjcl.c

Implementation of a small Canon BJC command-generation library. It serializes BJC escape commands to a Ghostscript `stream`.

Key behavior:
- Utility helpers write bytes, high/low and low/high 16-bit fields, and generic ESC-command envelopes.
- Emits single-character commands: LF, FF, CR.
- Emits session commands: initialize/reset, set initial condition, compression, print method, short print method, media supply, and cartridge identification.
- Emits page commands: page margins, extended margins, and page ID.
- Emits image commands: raster resolution, raster skip, CMYK image data, move lines, move-line unit, image format, continue image, and indexed image.

Notable dependencies:
- Includes `std.h` and the public BJC command interface `gdevbjcl.h`.
- Uses Ghostscript stream output APIs: `spputc` and `sputs`.

Research notes:
- The implementation is deliberately thin and generally trusts callers to pass valid values/ranges documented in the header.
- Several implementation names do not match prototypes in `gdevbjcl.h`: the source defines `bjc_put_set_initial` and `bjc_put_set_compression`, while the header declares `bjc_put_initial_condition` and `bjc_put_compression`. Unless macros elsewhere bridge these names, this is an API mismatch.
- The header declares `bjc_put_photo_image`, but this file does not implement it.
