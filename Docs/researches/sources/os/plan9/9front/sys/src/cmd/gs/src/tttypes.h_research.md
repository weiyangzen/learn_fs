# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/tttypes.h

Internal FreeType-derived common type header for Ghostscript TrueType code.

Key points:
- Includes `ttconfig.h` and the public `tttype.h`.
- Defines compact aliases: `Byte`, `UShort`, `Short`, `ULong`, `Long`, `Fixed`, `Int`, `Integer`, and pointer aliases.
- Selects `Fixed` from `int` or `long` based on `SIZEOF_INT` / `SIZEOF_LONG`.
- Defines `Pointer`, coordinate pointer types, and touch-table pointer type.
- Supplies `Bool`, `TRUE`, `FALSE`, and `NULL` fallbacks.
- Defines TrueType rounding mode constants.
- Defines point flag masks for on-curve and touched-X/Y state.
- Defines generic `SUCCESS` / `FAILURE` constants and `MIN`, `MAX`, `ABS` macros.
- Defines `HANDLE_*` conversion macros for the typed wrapper handles declared in `tttype.h`.

Dependencies and interactions:
- Used by FreeType-derived internals that need simple scalar aliases and access to opaque handle internals.
- Bridges public `TT_*` types to internal `PFace`, `PInstance`, `PGlyph`, and charmap structures.

Research relevance:
- This header is the internal type glue for Ghostscript’s bundled TrueType subsystem and is important for understanding fixed-point size assumptions and handle casting.
