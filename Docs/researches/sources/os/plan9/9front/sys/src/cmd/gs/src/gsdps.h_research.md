# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdps.h

This header exposes Display PostScript library facilities.

It includes `gsiparm2.h` for device-source image parameters and declares view clipping functions:
- `gs_initviewclip`
- `gs_eoviewclip`
- `gs_viewclip`
- `gs_viewclippath`

Implementation is in `gsdps.c`; additional DPS graphics operators are in `gsdps1.c`.
