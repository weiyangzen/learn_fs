# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxttfb.c

Bridge between Ghostscript Type 42 fonts and the bundled TrueType interpreter/outliner. It adapts Ghostscript font data, memory management, and paths to the TrueType interpreter interfaces.

Key behavior:
- Defines GC behavior for `gx_ttfReader`; `pfont` and `glyph_data` are intentionally not enumerated because they may point from global memory to local memory and must be cleared before GC.
- Implements `ttfReader` methods: EOF, read, seek, tell, error, glyph loading, and glyph release.
- `gx_ttfReader__LoadGlyph` asks the Type 42 font for a glyph outline through `get_outline`, maintains one extra glyph buffer, and returns it to the TrueType outliner.
- `gx_ttfReader__Reset`, `create`, `destroy`, and `set_font` manage reader lifecycle.
- `ttfFont__create` adapts Ghostscript memory to `ttfMemory`, obtains a TrueType interpreter and spot analyzer from the font directory, allocates `ttfFont`, and initializes debug callbacks.
- `ttfFont__destroy` finalizes the TrueType font and releases interpreter/analyzer resources.
- `ttfFont__Open_aux` decomposes the character matrix, opens a TrueType font, maps interpreter errors to Ghostscript errors, and records warnings for bad instructions or patented interpreter needs.
- `gx_ttfExport` converts outliner callbacks into `gx_path` operations: move, line, curve, close, and set width.
- `gx_ttf_outline` builds a glyph outline, selecting TT grid fitting, design-grid rendering, autohinting fallback, or unhinted output based on `gs_currentgridfittt`.
- `grid_fit` is an unfinished autohinting path that uses the Type 1 hinter over a generated TrueType outline and spot analyzer stems.

Notable dependencies:
- Type 42 font internals: `gxfont42.h`.
- TrueType interpreter/outliner headers: `gxttfb.h`, `ttfmemd.h`, `ttfoutl.h`.
- Path and hinting: `gxpath.h`, `gzpath.h`, `gxhintn.h`, `gzspotan.h`.
- Ghostscript memory and font APIs: `gsstruct.h`, `gsfont.h`.

Research notes:
- `gx_ttfReader__Read` cannot handle positive continuation from `string_proc`; it returns `gs_error_unregistered` for that unimplemented loop case.
- `ttfFont__create` has early returns after allocating `gx_ttfMemory` if interpreter or spot analyzer acquisition fails, with no visible cleanup of `m`; callers should treat this legacy path carefully.
- Warnings for bad instructions and patented behavior are emitted once per base font.
- There is a typo in the warning string: “fhe glyph index”.
