# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttfoutl.h

Purpose: public interface for Ghostscript’s TrueType instruction/outlining adapter.

Key contents:
- Forward-declares `TFace`, `TInstance`, `TExecution_Context`, and `ttfInterpreter`.
- Defines `FloatMatrix`, `FloatPoint`, `F26Dot6`, and `F26Dot6Point`.
- Defines abstract `ttfMemory` allocator interface.
- Defines `ttfInterpreter` capsule with execution context, compound-glyph usage stack, lock count, and memory interface.
- Defines `FontError` enum.
- Defines abstract `ttfReader` interface for EOF/read/seek/tell/error/glyph load/release.
- Defines `ttfFont` with sfnt table pointers, metrics/config fields, face/instance/context/interpreter pointers, and debug callbacks.
- Declares font and interpreter lifecycle functions.
- Defines abstract `ttfExport` outline sink callbacks.
- Defines `ttfGlyphOutline` and `ttfOutliner`, plus outliner init/outline/draw APIs.

Dependencies: Ghostscript base types and TrueType implementation structs declared elsewhere.

Integration notes: this is the main boundary between Ghostscript font code and the TrueType parser/hinter.

Risks: the memory and reader interfaces are callback-driven; implementers must honor allocation ownership and glyph buffer release contracts.
