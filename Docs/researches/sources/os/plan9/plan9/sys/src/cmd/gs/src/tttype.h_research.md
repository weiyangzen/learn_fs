# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/tttype.h

FreeType-derived public TrueType high-level API header, modified in Ghostscript by removing the TrueType instruction interpreter.

Key points:
- Defines public `TT_` scalar types, fixed-point types, vectors, matrices, outlines, bounding boxes, glyph metrics, raster maps, and TrueType table structures.
- Exposes typed opaque handles for engine, stream, face, instance, glyph, and charmap objects via single-pointer structs to preserve type checking.
- Declares face management APIs: initialize/finalize engine, open faces/collections, query properties, read font/table data, flush/close faces.
- Declares instance APIs for resolutions, character sizes, pixel sizes, transform flags, metrics, generic user pointers, and cleanup.
- Declares glyph APIs for creating/loading glyphs, retrieving outlines/metrics, rendering bitmaps or pixmaps, and outline allocation/copy/render/transform helpers.
- Declares charmap/name-table enumeration and lookup APIs.
- Defines callback registration for glyph outline loading.
- Defines grouped error constants for API failures, missing tables, memory/file errors, glyph loader problems, bytecode interpreter errors, internal failures, and raster errors.

Dependencies and interactions:
- Included by `tttypes.h` and other TrueType support code.
- Depends on architecture macros such as `ARCH_LOG2_SIZEOF_LONG` and `ARCH_LOG2_SIZEOF_INT` for fixed-size type selection.
- API surface is FreeType 1-style and supports Ghostscript’s embedded TrueType/font handling path.

Research relevance:
- This is the main public contract for the bundled TrueType engine used by Ghostscript’s font subsystem.
