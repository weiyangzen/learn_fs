# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttload.c

## Role

`ttload.c` loads the small subset of TrueType tables needed by this scaler’s interpreter and instance setup.

## Main Responsibilities

- `Load_TrueType_MaxProfile(PFace face)` reads the `maxp` table and fills `face->maxProfile`.
- `Load_TrueType_CVT(PFace face)` reads the raw control value table into `face->cvt`.
- `Load_TrueType_Programs(PFace face)` loads optional `fpgm` font program bytes and optional `prep` CVT program bytes.

## Important Implementation Details

- Table offsets and lengths come from `ttfFont` fields such as `t_maxp`, `t_cvt_`, `t_fpgm`, and `t_prep`.
- Data is read through `ttfReader` helper macros from `ttload.h`.
- Allocations use the Ghostscript `ttfMemory` allocator reachable through `font->tti->ttf_memory`.
- `maxp` values are also normalized into face-level maxima:
  - `numGlyphs`
  - `maxPoints`
  - `maxContours`
  - `maxComponents`
- The font program is optional. The prep program may be absent, in which case CVT program size is zero.
- CVT size is derived from table length divided by two, because entries are signed shorts.

## Cross-File Relationships

- Loaded face fields are consumed by `ttobjs.c` during `Face_Create`, `Context_Create`, `Instance_Create`, `Instance_Init`, and `Instance_Reset`.
- CVT data loaded here is copied/scaled into instance CVT arrays before prep or glyph programs execute.
- Uses type definitions from `ttobjs.h` and `tttables.h`.

## Notable Risks / Review Notes

- The implementation assumes directory entries have already been populated in `ttfFont`; this file does not validate table checksums or directory structure.
- Reads stop on reader EOF for CVT entries but do not otherwise enforce exact table completeness.
- Only `maxp`, `cvt`, `fpgm`, and `prep` are actively loaded in this file; many loader prototypes exist elsewhere or are unused by this reduced path.
