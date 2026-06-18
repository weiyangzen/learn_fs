# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/tttables.h

TrueType table structure declarations used by the FreeType-derived loader/object code.

Key points:
- Defines TrueType Collection header `TTTCHeader`.
- Defines table directory header `TTableDir`.
- Defines table directory entry `TTableDirEntry`.
- Defines cmap directory and entry structures:
  - `TCMapDir`
  - `TCMapDirEntry`
- Defines maximum profile table `TMaxProfile`, including glyph counts and maxima for points, contours, components, zones, twilight points, storage, function defs, instruction defs, stack elements, instruction size, and component depth.
- Defines gasp flags:
  - `GASP_GRIDFIT`
  - `GASP_DOGRAY`
- Defines gasp range/table structures:
  - `GaspRange`
  - `TGasp`
- Notes that head, hhea, OS/2, and post tables are defined elsewhere.
- Defines horizontal metrics structure `TLongHorMetric`.
- Defines loca table structure `TLoca`.
- Defines name record and name table structures:
  - `TNameRec`
  - `TName_Table`
- Wraps declarations for C++.

Dependencies and interactions:
- Includes `tttypes.h`.
- `TMaxProfile` is used directly by `ttload.c`, `ttobjs.c`, and `ttobjs.h`.
- Several declared table types support broader loader APIs declared in `ttload.h`, even though this group’s implementation only loads a subset.

Research relevance:
- Provides the on-disk table metadata shapes that drive allocation limits and table parsing for the TrueType interpreter support code.
