# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor2.h

## Purpose
Public client interface for Level 2 color facilities.

## Key Contents
- Includes Indexed color and pattern type declarations.
- Declares general color-space and color APIs:
  - `gs_currentcolorspace`,
  - `gs_setcolorspace`,
  - `gs_currentcolor`,
  - `gs_setcolor`.
- Declares CRD accessors:
  - `gs_currentcolorrendering`,
  - `gs_setcolorrendering`.
- Declares high-level device support API `gs_includecolorspace`.

## Dependencies
Requires `gscspace.h` and `gsmatrix.h`; includes `gscindex.h` and `gsptype1.h`.

## Research Notes
This is the main public bridge from normal color operators to CIE CRD handling.
