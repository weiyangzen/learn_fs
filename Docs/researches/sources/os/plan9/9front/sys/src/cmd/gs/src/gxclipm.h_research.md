# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclipm.h

Small declaration header for the Ghostscript mask clip device.

Key behavior:
- Includes `gxmclip.h` for `gx_device_mask_clip` and related mask clipping structures.
- Declares the exported `gs_mask_clip_device` descriptor implemented in `gxclipm.c`.

Dependencies:
- Requires Ghostscript structure/device/memory-device definitions before or through `gxmclip.h`.

Research notes:
- The header is intentionally minimal; construction and operational logic are provided by the generic mask clipping layer and `gxclipm.c`.
