# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttfoutl.h

TrueType instruction interpreter and outline extraction interface.

Key declarations:
- Forward-declares `TFace`, `TInstance`, `TExecution_Context`, and `ttfInterpreter`.
- Defines `FloatMatrix`, `FloatPoint`, `F26Dot6`, and `F26Dot6Point`.
- Defines abstract `ttfMemory` allocator API with byte allocation, structured allocation, and free callbacks.
- Defines `ttfInterpreter` capsule with execution context, subglyph usage stack, lock, and memory pointer.
- Defines `FontError` values covering missing tables/names, memory failure, unimplemented data, cmap/glyph absence, bad font data, patented code, and bad instructions.
- Defines abstract `ttfReader` callbacks:
  - EOF/read/seek/tell/error
  - glyph load/release
- Defines `ttfFont` table-pointer metadata, units/flags/counts/metric table info, interpreter objects, and debug callbacks.
- Declares `ttfFont__init`, `ttfFont__finit`, and `ttfFont__Open`.
- Defines `ttfExport` callbacks for moves, lines, curves, close, points, width, and debug paint.
- Declares interpreter obtain/release routines.
- Defines `ttfGlyphOutline` and `ttfOutliner`.
- Declares `ttfOutliner__init`, `ttfOutliner__Outline`, and `ttfOutliner__DrawGlyphOutline`.

Dependencies and interactions:
- Included by TrueType parser/adapter code and Ghostscript consumers that provide reader/export adapters.

Research relevance:
- Primary public interface for TrueType outline extraction in this Ghostscript source subset.
