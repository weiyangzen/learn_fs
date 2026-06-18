# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip2.h

## Purpose
Declares the tiled mask clipping device interface.

## Main Responsibilities
- Aliases `gx_device_tile_clip` to `gx_device_mask_clip`.
- Provides the tile-clip structure descriptor macro.
- Declares initialization and phase-setting procedures.

## Key API
- `tile_clip_initialize(...)`: creates a tile clipping wrapper from a `gx_strip_bitmap`, target device, phase, and allocator.
- `tile_clip_set_phase(...)`: updates the tile phase used by repeated tile clipping.

## Dependencies
- Includes `gxmclip.h`, since tiled clipping reuses the generic mask clip structure.

## Research Notes
The header makes explicit that tile clipping is structurally identical to mask clipping. The distinction is behavioral and lives in the device procedure table from `gxclip2.c`.
