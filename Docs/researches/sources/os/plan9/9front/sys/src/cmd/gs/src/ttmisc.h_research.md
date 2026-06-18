# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttmisc.h

Common compilation-context header for FreeType-derived TrueType modules.

Key points:
- Includes Ghostscript portability and math headers:
  - `gx.h`
  - `string_.h`
  - `math_.h`
  - `std.h`
- Includes `tttypes.h`.
- Maps `MulDiv` to `ttMulDiv`.

Dependencies and interactions:
- Included first by `ttinterp.c`, `ttload.c`, and `ttobjs.c`.
- Bridges Ghostscript’s core portability layer with the imported TrueType code.

Research relevance:
- Small but important adapter header that normalizes the build environment for this FreeType-derived TrueType subsystem.
