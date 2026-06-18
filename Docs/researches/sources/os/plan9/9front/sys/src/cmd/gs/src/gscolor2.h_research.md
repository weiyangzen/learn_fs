# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor2.h

## Role

`gscolor2.h` declares the Ghostscript Level 2 color API for general color spaces, current color, CIE color rendering, and device color-space inclusion.

This is rendering/color API infrastructure, not filesystem code.

## Public API

- `gs_currentcolorspace`
- `gs_setcolorspace`
- `gs_currentcolor`
- `gs_setcolor`
- `gs_currentcolorrendering`
- `gs_setcolorrendering`
- `gs_includecolorspace`

## Dependencies

Includes `gscindex.h` and `gsptype1.h`; requires `gscspace.h` and `gsmatrix.h` context.

## Important Contract

The header notes that `setcolorspace` and `setcolor` copy only the top level of their structure arguments, so heap-allocated caller structures may be freed after setting them, but referenced subobjects must obey the color-space reference-counting rules.

## Notable Risks

CRD type is forward-declared here for public use; concrete CRD layout is in `gscie.h`.
