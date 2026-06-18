# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip2.h

Public internal interface for Ghostscript tiled mask clipping.

Key behavior:
- Includes `gxmclip.h` and aliases `gx_device_tile_clip` to `gx_device_mask_clip`, since tiled clipping reuses the same storage layout.
- Aliases the GC structure descriptor to `st_device_mask_clip`.
- Provides `private_st_device_tile_clip()` as a harmless top-level dummy declaration for compilation compatibility.
- Declares `tile_clip_initialize` for constructing a tiled mask clip device from a strip bitmap and target device.
- Declares `tile_clip_set_phase` for updating tile alignment during tiling loops.

Dependencies:
- Depends on `gx_device_mask_clip`, `gx_strip_bitmap`, `gx_device`, and `gs_memory_t` from Ghostscript device/mask infrastructure.

Research notes:
- This header exposes tiled clipping as a distinct device concept while deliberately sharing the mask clip implementation layout.
