# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/tttables.h

## Role

`tttables.h` defines C structures for selected TrueType/OpenType table records used by the FreeType-derived scaler.

## Main Responsibilities

- Defines TrueType Collection header representation.
- Defines table directory and table directory entry structures.
- Defines cmap directory and cmap directory entry structures.
- Defines `TMaxProfile` for the `maxp` table.
- Defines `gasp` table flags and range structures.
- Defines horizontal metric records.
- Defines `loca` and `name` table structures.

## Important Implementation Details

- `TMaxProfile` is the most important structure for this group. `ttload.c` reads it, and `ttobjs.c` uses its maximum values to allocate interpreter stack, point zones, twilight zone, storage, FDEF/IDEF arrays, and instruction capacity.
- Some table types are declared here even though this grouped implementation does not load them directly.
- The header intentionally leaves `head`, `hhea`, `OS/2`, and `post` table definitions to other headers.

## Cross-File Relationships

- Included by `ttobjs.h`.
- `ttload.c` fills `TMaxProfile` through `Load_TrueType_MaxProfile`.
- `ttobjs.c` consumes max profile values during face, instance, and context setup.

## Notable Risks / Review Notes

- These are raw table-shape definitions. Validation and endian conversion happen in loader code, not here.
- The declared table surface is broader than the subset used by `Face_Create` in `ttobjs.c`.
