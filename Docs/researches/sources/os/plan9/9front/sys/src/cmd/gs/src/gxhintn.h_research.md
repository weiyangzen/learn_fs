# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhintn.h

## Role

`gxhintn.h` declares the Type 1 hinter data model and public entry points implemented by `gxhintn.c`.

This is font rendering infrastructure, not filesystem code.

## Main Definitions

- Feature switches: `FINE_STEM_COMPLEXES`, `ALIGN_BY_STEM_MIDDLE`, `OPPOSITE_STEM_COORD_BUG_FIX`, and `TT_AUTOHINT_TOPZONE_BUG_FIX`.
- Capacity constants: `T1_MAX_STEM_SNAPS`, `T1_MAX_ALIGNMENT_ZONES`, `T1_MAX_CONTOURS`, `T1_MAX_POLES`, and `T1_MAX_HINTS`.
- Coordinate types: `t1_glyph_space_coord`, `t1_hinter_space_coord`, and `int19`.
- Enums for hint type, pole type, zone type, and alignment status.

## Data Structures

- `double_matrix` and `fraction_matrix` hold floating and fixed/fraction transform forms.
- `t1_pole` represents an outline point/control point with source and aligned coordinates, type, contour index, and per-axis alignment status.
- `t1_hint` represents one stem/dot hint with source/aligned boundaries, quality, active range link, stem3 index, and side mask.
- `t1_hint_range` links active ranges of hints to pole intervals.
- `t1_zone` represents a BlueValues-style top or bottom alignment zone.
- `t1_hinter` owns all persistent state for one glyph import/hint/export cycle, including matrices, origin, widths, contour arrays, hints, zones, stem snap arrays, flex state, font metrics, grid fitting state, output path, and allocator.

## Public Interface

- Lifecycle and setup: `t1_hinter__init`, `t1_hinter__set_mapping`, `t1_hinter__set_font_data`, `t1_hinter__set_font42_data`.
- Path import: `t1_hinter__sbw`, `sbw_seac`, `rmoveto`, `rlineto`, `rcurveto`, `setcurrentpoint`, `closepath`.
- Flex import: `flex_beg`, `flex_point`, `flex_end`.
- Hint import: `hint_mask`, `drop_hints`, `dotsection`, `hstem`, `vstem`, `overall_hstem`, `hstem3`, `vstem3`.
- Finalization/query: `endchar`, `endglyph`, and `is_x_fitting`.

## Notable Risks

- The struct exposes many internal fields directly; callers must follow the intended interpreter call sequence.
- Comments contain minor inaccuracies/typos, including `align_to_pixels` described as false meaning align to integral pixels.
- The `hstem3` prototype parameter names mix `x` and `y` names, although the types are all `fixed`; this is harmless to C compilation but confusing to readers.
