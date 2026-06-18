# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfmain.c

FreeType interface adapter for Ghostscript TrueType outline extraction.

Key behavior:
- Defines fixed/floating transform helpers for F26.6 and 16.16 values.
- Maps SFNT table names to `ttfFont` table pointer fields.
- Implements `TT_Set_Instance_CharSizes`, setting instance scale, ppem, point size, integer scaling, and resetting the instance.
- `ttfInterpreter__obtain` creates or refcounts a shared interpreter capsule and allocates execution context.
- `ttfInterpreter__release` decrements lock, frees usage buffer, execution context, interpreter object, and memory wrapper.
- `ttfFont__init`/`ttfFont__finit` initialize and release font face/instance/context resources.
- `ttfFont__Open`:
  - handles TTC collections and plain TrueType headers
  - scans table directory
  - loads core table metadata from `head`, `maxp`, `hhea`, optional `vhea`
  - allocates compound-glyph usage storage
  - creates FreeType-derived face/context/instance structures
  - initializes CVT and instance metrics
  - maps FreeType errors to `FontError` values
- Glyph setup/teardown uses `Context_Load`/`Context_Save` and instruction-control logic.
- Provides helpers for mounting glyph zones, initializing subglyph records, and copying current/original glyph coordinates.
- `ttfOutliner__init` stores reader/export/font/orientation state.
- `ttfOutliner__BuildGlyphOutlineAux`:
  - reads horizontal or vertical metrics
  - supports metrics-only queries when outlines are disabled
  - loads glyph data through `ttfReader::LoadGlyph`
  - parses simple and compound glyphs
  - enforces point/contour limits
  - expands repeat flags and decodes relative X/Y coordinates
  - recursively builds compound subglyph outlines with bounded nesting storage
  - handles component transforms, anchor/offset placement, and `USE_MY_METRICS`
  - optionally runs glyph instructions through `Context_Run`
  - adds phantom points for hinting and width adjustment
  - reports malformed fonts, patented instructions, memory failures, and bad instructions
- `ttfOutliner__DrawGlyphOutline`:
  - exports width first
  - optionally exports raw points
  - converts TrueType quadratic curves to cubic Bezier callbacks
  - emits move/line/curve/close callbacks
  - skips 1- and 2-point contours
  - contains an `AVECTOR_BUG` workaround for outlier points beyond expanded bbox bounds
- `ttfOutliner__Outline` wraps glyph start/build/stop, applies design-grid post-transform scaling, and returns outline status without drawing directly.

Dependencies and interactions:
- Includes `ttmisc.h`, `ttfoutl.h`, `ttfmemd.h`, `ttfinp.h`, `ttfsfnt.h`, `ttobjs.h`, `ttinterp.h`, and `ttcalc.h`.
- Consumes abstract `ttfReader` and `ttfExport` APIs declared in `ttfoutl.h`.
- Uses FreeType-derived context/instance/face APIs and Ghostscript GC descriptors from `ttfmemd.c`.

Research relevance:
- Main bridge between TrueType/SFNT data and Ghostscript outline callbacks. It is the highest-level TrueType file in this group.
