# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont1.h

## Purpose
Defines Ghostscript Type 1 and Type 2 font data structures and procedure interfaces.

## Main Types
- `gs_type1_data_procs_t`: callback table for glyph data, Subr data, `seac` data, and OtherSubr stack interaction.
- `gs_type1_data`: Type 1/2 interpreter data, callback data, parent Type 9 font pointer, encryption length, subroutine biases, width defaults, random seed, and hinting parameters.
- `gs_font_type1`: `gs_font_base_common` plus `gs_type1_data`.

## Hinting Data
Stores Type 1 hint tables and parameters:
- Blue values/family blues/other blues,
- standard stem widths,
- stem snap arrays,
- weight vector,
- force bold, language group, expansion and rounding fields.

## Declared Procedures
- `gs_type1_glyph_info`
- `gs_type1_piece_codes`

## Integration With Font Copying
`gxfcopy.c` uses this header to:
- copy glyph CharString bytes,
- copy Subrs/GlobalSubrs,
- invoke Type 1 glyph info,
- interpret copied outlines,
- detect `seac` pieces.
