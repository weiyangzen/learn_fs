# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxmclip.c

Implementation of Ghostscript mask clipping device initialization and GC support.

Key behavior:
- Defines the public structure descriptor for `gx_device_mask_clip`.
- Enumerates and relocates pointers inside the mask clip device, including embedded strip bitmap, embedded memory device, and forwarding-device prefix.
- Relocation adjusts memory-device line pointers specially because they point into the mask clipping device’s embedded buffer.
- `gx_mask_clip_initialize` initializes a forwarding mask clip device against a target, copies dimensions/color info, sets phase, creates an embedded monochrome memory device, and sizes its buffer within a small fixed internal buffer.
- If the mask tile is too wide to buffer even one scanline, it sets `mdev.base = 0` and returns success so callers can use a slower fallback.

Notable dependencies:
- Device and memory device APIs from `gxdevice.h` and `gxdevmem.h`.
- Structure definition from `gxmclip.h`.

Research notes:
- The implementation avoids separate allocation for the tile buffer by using storage embedded in `gx_device_mask_clip`.
- The too-wide case is intentional and handled by header-side copy-mono fallback logic.
