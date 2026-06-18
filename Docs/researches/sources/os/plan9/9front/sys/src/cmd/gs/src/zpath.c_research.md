# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zpath.c

## Purpose
Implements basic PostScript path construction and clipping operators.

## Key Functions
- `znewpath()`, `zcurrentpoint()`, `zmoveto()`, `zrmoveto()`, `zlineto()`, and `zrlineto()` manage simple path segments.
- `zcurveto()` and `zrcurveto()` add Bezier segments.
- `zclosepath()`, `zinitclip()`, `zclip()`, and `zeoclip()` handle path closure and clipping.
- `common_to()` and `common_curve()` parse numeric operands and dispatch to graphics APIs.

## Important Behavior
- Numeric path operands are parsed as doubles and passed to graphics state path APIs.
- Successful path construction pops consumed operands.
- `currentpoint` pushes two reals.

## Research Notes
Core interpreter path API glue.
