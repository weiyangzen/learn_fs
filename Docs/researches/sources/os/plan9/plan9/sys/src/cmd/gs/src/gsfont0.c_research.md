# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont0.c

## Role

Composite FontType 0 support for defining and scaling composite fonts.

## Main Data

Provides the GC structure descriptor for `gs_font_type0`, including `Encoding`, `FDepVector`, and either `SubsVector` or `CMap` depending on `FMapType`.

## Control Flow

`gs_type0_adjust_matrix` scans descendant fonts for composites, copies `FDepVector`, and applies `gs_makefont` to composite descendants using the provided matrix. `gs_type0_define_font` applies this adjustment when a non-identity `FontMatrix` is used. `gs_type0_make_font` performs the same adjustment after scaling.

## Dependencies

Depends on composite font structures in `gxfont0.h`, font directory functions, matrix/device headers, and Ghostscript GC descriptor macros.

## Notes

The adjustment is skipped for identity matrices and for descendant vectors with no composite descendants.
