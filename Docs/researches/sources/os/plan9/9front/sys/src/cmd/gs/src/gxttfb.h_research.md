# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxttfb.h

Public bridge header for Ghostscript’s Type 42 / TrueType interpreter integration.

Key contents:
- Includes `ttfoutl.h`.
- Forward-declares `gx_ttfReader` and `gs_font_type42`.
- Defines `struct gx_ttfReader_s`, embedding `ttfReader` plus stream position, error flag, loaded extra glyph index, font pointer, allocator, and glyph-data buffer.
- Documents that `pfont` and `glyph_data` may temporarily point from global memory to local memory and must be null/reset during GC-sensitive periods.
- Declares reader lifecycle and binding functions.
- Declares `ttfFont__create`, `ttfFont__destroy`, `ttfFont__Open_aux`, and `gx_ttf_outline`.

Dependencies:
- TrueType outliner/interpreter types from `ttfoutl.h`.
- Ghostscript font, memory, glyph-data, matrix, scale, and path types from surrounding includes.

Research notes:
- This header defines the ownership boundary between Ghostscript memory management and the TrueType interpreter’s callback-oriented API.
- The GC warning in the struct comment is important: callers must avoid leaving local-memory pointers visible from globally allocated reader objects.
