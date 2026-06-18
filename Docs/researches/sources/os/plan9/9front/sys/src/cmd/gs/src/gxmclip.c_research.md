# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxmclip.c

Implementation of Ghostscript mask clipping device initialization and GC support.

Key behavior:
- Defines the public structure descriptor for `gx_device_mask_clip`.
- Enumerates and relocates pointers inside the mask clip device, including embedded strip bitmap, embedded memory device, and forwarding-device prefix.
- Relocation adjusts memory-device line pointers specially because they point into the mask clip device’s own embedded buffer.
- `gx_mask_clip_initialize` initializes a forwarding mask clip device against a target, sets dimensions/color info/phase, creates an embedded monochrome memory device for tile buffering, and sizes the buffer to fit within a small fixed internal buffer.
- If the mask tile is too wide to buffer even one scanline, it sets `mdev.base = 0` and returns success, leaving callers to use a slower fallback.

Notable dependencies:
- Device and memory device APIs from `gxdevice.h` and `gxdevmem.h`.
- Structure definition from `gxmclip.h`.

Research notes:
- The implementation uses an embedded buffer rather than allocating tile-buffer memory separately.
- The “too wide” case is intentionally supported by punting to default slow `copy_mono` behavior via the header macro.
