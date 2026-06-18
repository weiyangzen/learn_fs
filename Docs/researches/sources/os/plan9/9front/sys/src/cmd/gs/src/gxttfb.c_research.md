# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxttfb.c

Bridge between Ghostscript Type 42 font objects and the bundled TrueType interpreter/outliner.

Key behavior:
- Defines GC descriptor for `gx_ttfReader`, intentionally not enumerating `pfont` or `glyph_data` because they may point from global memory to local memory while the interpreter is active.
- Implements `ttfReader` callbacks: EOF, read, seek, tell, error, load glyph, release glyph.
- `gx_ttfReader__Read` reads from either a loaded glyph buffer or the Type 42 font `string_proc`; multi-part string reads are explicitly unimplemented.
- `gx_ttfReader__LoadGlyph` uses `pfont->data.get_outline` and keeps one extra glyph buffer at a time.
- `gx_ttfReader__create`, `destroy`, and `set_font` manage reader lifetime and font binding.
- Debug and warning helpers route TrueType interpreter messages and one-time bad-instruction/patent warnings.
- `gx_ttfMemory` adapts Ghostscript allocators to the TrueType interpreter memory interface.
- `ttfFont__create`, `ttfFont__destroy`, and `ttfFont__Open_aux` create/open interpreter font state, acquire/release shared interpreter and spot-analyzer resources, and map interpreter errors to Ghostscript errors.
- `decompose_matrix` separates glyph size, subpixel origin, post-transform, design-grid decisions, pixel alignment, and grid-fitting mode.
- `gx_ttfExport` adapts outliner callbacks to Ghostscript paths, optionally monotonizing curves for autohinting.
- `grid_fit` uses the Type 1 hinter and spot analyzer as an autohint fallback for Type 42 outlines.
- `gx_ttf_outline` runs the outliner, handles patented/bad-instruction fallback modes, optionally autohints, and appends the resulting outline to a `gx_path`.

Dependencies:
- Type 42 font internals from `gxfont42.h`.
- TrueType interpreter headers: `ttfoutl.h`, `ttfmemd.h`.
- Path, cache, matrix, paint, imager, and Type 1 hinting APIs.
- Spot analyzer from `gzspotan.h`.

Research notes:
- Grid fitting modes are controlled by `gs_currentgridfittt`: no fitting, TT interpreter, design-grid autohint, or TT with autohint fallback.
- `ttfFont__create` has early-return paths after allocating the memory adapter that do not visibly free it if interpreter/spot-analyzer acquisition fails.
- Reader destruction assumes no outstanding loaded glyph buffer; normal flows reset/release it, but `destroy` itself does not call reset.
