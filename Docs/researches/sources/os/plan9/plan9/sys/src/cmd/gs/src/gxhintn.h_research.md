# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhintn.h

Purpose: public/internal header for the Type 1 hinter implemented in `gxhintn.c`.

Key definitions:
- Compile-time feature flags for fine stem complexes, stem-middle alignment, opposite-coordinate bug fix, and TrueType autohint top-zone fix.
- Capacity constants: stem snaps, alignment zones, contours, poles, and hints.
- Coordinate types: `t1_glyph_space_coord`, `t1_hinter_space_coord`, and `int19`.
- Enums for hint type (`hstem`, `vstem`, `dot`), pole type, zone type, and alignment strength.
- Matrix structs: `double_matrix` and `fraction_matrix`.
- Core records: `t1_pole`, `t1_hint`, `t1_hint_range`, `t1_zone`, and `t1_hinter`.

`t1_hinter` contents:
- Transform state, glyph origin/width/current-point state, grid-fit flags, blue-zone/stem data, pole/hint/contour arrays, font metrics, ForceBold/seac flags, and output path/memory pointers.
- Embedded arrays provide common-case storage, with pointers allowing growth.

Public API:
- Initialization and configuration: `t1_hinter__init`, `t1_hinter__set_mapping`, `t1_hinter__set_font_data`, `t1_hinter__set_font42_data`.
- Charstring drawing commands: `sbw`, `rmoveto`, `rlineto`, `rcurveto`, `setcurrentpoint`, `closepath`.
- Flex, hint, and stem commands.
- Completion/accessors: `endchar`, `endglyph`, `is_x_fitting`.

Dependencies:
- Requires Ghostscript fixed/matrix/memory types from included surrounding headers; directly includes `stdint_.h`.

Research notes:
- This header exposes a stateful, procedural interface intended to be called by Type 1/Type 2 charstring interpreters.
