# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/tttype.h

FreeType 1 high-level public API header bundled in Ghostscript’s TrueType support.

Key points:
- Defines public `TT_*` scalar, fixed-point, vector, matrix, outline, bounding-box, raster-map, metrics, face-property, and handle types.
- Uses architecture macros such as `ARCH_LOG2_SIZEOF_LONG` / `ARCH_LOG2_SIZEOF_INT` to choose 32-bit fixed-point storage.
- Exposes handle wrappers for engine, stream, face, instance, glyph, and charmap objects using one-field structs for compile-time type separation.
- Declares lifecycle APIs: `TT_Init_FreeType`, `TT_Done_FreeType`, face open/close/flush, instance creation/destruction, glyph creation/destruction.
- Declares font access APIs for properties, raw table data, charmaps, names, glyph loading, glyph metrics, outlines, bitmap/pixmap rendering, outline allocation/copy/rendering, and matrix/vector transforms.
- Defines load flags `TTLOAD_SCALE_GLYPH`, `TTLOAD_HINT_GLYPH`, and `TTLOAD_DEFAULT`.
- Defines `MAKE_TT_TAG` for TrueType table tags.
- Defines callback ID and callback type for glyph outline loading.
- Defines the main `TT_Error` code space for API, table, memory, file, glyph loader, bytecode interpreter, internal, and raster errors.

Dependencies and interactions:
- Included by `tttypes.h`, which adds internal typedefs and handle conversion macros.
- Used by Ghostscript’s FreeType-derived TrueType loader modules such as `ttload`, `ttobjs`, `tttables`, and interpreter support.
- Public structures are consumed by client-facing glyph/font code and by internal conversion helpers.

Research relevance:
- This is the public contract for the vendored FreeType 1 TrueType engine inside Ghostscript. It determines how fonts, glyphs, outlines, metrics, charmaps, and raster targets are represented across the old Ghostscript font bridge.
