# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxttfb.h

Header for the Ghostscript-to-TrueType interpreter bridge.

Key contents:
- Includes `ttfoutl.h`.
- Forward-declares `gx_ttfReader` and `gs_font_type42`.
- Defines `struct gx_ttfReader_s` as a `ttfReader` subclass with stream position, error state, one extra glyph buffer index, Type 42 font pointer, allocator, and `gs_glyph_data_t`.
- Declares reader lifecycle and font binding functions.
- Declares `ttfFont__create`, `ttfFont__destroy`, `ttfFont__Open_aux`, and `gx_ttf_outline`.

Research notes:
- The struct comment documents a GC hazard: the reader may live in global memory while `pfont` and `glyph_data` point to local memory, so those fields must be null when GC runs and are reset when the TrueType interpreter exits.
- This header is tightly paired with `gxttfb.c` and the bundled TrueType interpreter.
