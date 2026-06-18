# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrd.h

## Purpose
Public interface for CIE Color Rendering Dictionary creation.

## Key Contents
- Declares `gs_cie_render1_build`.
- Declares `gs_cie_render1_init_from`.
- Declares `gs_cie_render1_initialize`.
- Provides `gs_cie_render_client_data(pcrd)` l-value macro.

## Important Details
- Documents default handling for optional CRD parameter pointers.
- Documents that point/matrix/range/procedure values are copied, while RenderTable lookup table storage is only referenced.
- Documents optional cache copying when procedures are cache-backed and `pfrom_crd` is supplied.

## Dependencies
Includes `gscie.h`.

## Research Notes
Implementation is in `gscrd.c`.
