# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxmclip.h

Mask clipping device structure and helper interface.

Key contents:
- Documents mask clipping use for ImageType 3 images and Patterns that do not fill their bounding box.
- Defines a small aligned tile clip buffer size.
- Defines `gx_device_mask_clip`, a forwarding device containing a mask bitmap, embedded memory device, phase, and aligned buffer.
- Declares the structure descriptor and `gx_mask_clip_initialize`.
- Defines `setup_mask_copy_mono`, a macro used by copy-mono implementations to choose colors and fallback behavior for mask clipping.

Notable dependencies:
- `gxclip.h` and required device/memory-device definitions from including context.

Research notes:
- The structure is logically private, but exposed so clients can allocate instances directly.
- The phase is described as a device-space origin relative to the tile, opposite of graphics state phase semantics.
