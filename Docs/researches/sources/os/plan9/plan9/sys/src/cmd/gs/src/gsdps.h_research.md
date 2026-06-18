# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdps.h

## Role

`gsdps.h` is the client interface for Display PostScript facilities.

## Contents

It includes `gsiparm2.h` for device-source image parameter definitions and declares view-clipping APIs:

- `gs_initviewclip`
- `gs_eoviewclip`
- `gs_viewclip`
- `gs_viewclippath`

## Dependencies

Requires `gs_state` to be visible through normal Ghostscript client headers.

## Integration Notes

The header groups two DPS-related surfaces: device-source images through an include, and view clipping through declarations implemented in `gsdps.c`.

## Risks

No local implementation risk. Clients must link the corresponding DPS implementation objects when using view-clipping functions.
