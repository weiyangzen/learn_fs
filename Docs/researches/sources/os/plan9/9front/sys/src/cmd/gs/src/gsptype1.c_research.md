# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype1.c

Implements PatternType 1, the tiling-pattern implementation.

Main behavior:
- Defines PatternType 1 template/instance GC descriptors and type dispatch table.
- `gs_cspace_build_Pattern1` constructs Pattern color spaces with optional base spaces.
- `gs_pattern1_init` initializes PatternType 1 templates.
- `gs_makepattern`/`gs_pattern1_make_pattern` instantiate tiling patterns, save graphics state, compute tile stepping geometry, clip the tile, assign IDs, and account for colored versus uncolored PaintType behavior.
- `compute_inst_matrix` derives the stepping matrix and transformed bounding box.
- `clamp_pattern_bbox` limits huge pattern bounding boxes to the region that can actually affect the current page.
- `gs_pattern1_set_color` updates overprint behavior at set-color time; colored patterns conservatively mark all components as drawn.
- Implements bitmap/pixmap-derived pattern helpers used primarily by PCL.
- Defines device color types for colored patterns and masked uncolored variants: pure, binary halftone, and colored halftone.
- Implements pattern cache lookup and load methods.
- Pattern device colors cannot currently be serialized through the command list; write/read return errors.

Notable observations:
- `gs_cspace_build_Pattern1` appears to test `gs_color_space_num_components(pcspace)` while `pcspace` is still null; likely intended `pbase_cspace`.
- Pattern cache lookup accounts for internal pattern streams and dummy tiles.
