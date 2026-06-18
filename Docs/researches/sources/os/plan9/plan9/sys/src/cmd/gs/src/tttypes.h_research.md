# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/tttypes.h

FreeType-derived internal common type header for the TrueType engine.

Key points:
- Includes `ttconfig.h` and `tttype.h`.
- Defines internal scalar aliases: `Byte`, `UShort`, `Short`, `ULong`, `Long`, `Fixed`, `Int`, `Integer`, pointer aliases, `Pointer`, `PCoordinates`, and `PTouchTable`.
- Defines `Bool`, `TRUE`, `FALSE`, and `NULL` fallbacks.
- Defines `PStorage` based on Plan 9, pointer size, and integer/long size; Plan 9 amd64 uses `unsigned long long *`, other Plan 9 builds use `unsigned int *`.
- Defines TrueType rounding constants and touch flag masks.
- Defines simple `SUCCESS`/`FAILURE` constants and `MIN`, `MAX`, `ABS` macros.
- Provides handle conversion macros from public `TT_*` handles to internal pointer types such as `PEngine_Instance`, `PFace`, `PInstance`, `PGlyph`, and `PCMapTable`.

Dependencies and interactions:
- Internal TrueType implementation code uses this to bridge public typed handles to internal engine structs.
- The Plan 9-specific `PStorage` branch is the local portability change most relevant to this source tree.

Research relevance:
- Establishes internal portability assumptions for the bundled TrueType engine, including pointer-sized storage handling.
