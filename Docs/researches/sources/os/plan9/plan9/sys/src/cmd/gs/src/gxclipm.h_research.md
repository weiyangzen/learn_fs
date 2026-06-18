# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclipm.h

## Purpose
Declares the exported mask clipping device descriptor.

## Main Responsibilities
- Includes `gxmclip.h`.
- Exposes `extern const gx_device_mask_clip gs_mask_clip_device`.

## Dependencies
Requires the mask clipping structure definitions from `gxmclip.h`.

## Research Notes
This is a narrow public/internal bridge: users instantiate or reference the mask clipping device implemented in `gxclipm.c`.
