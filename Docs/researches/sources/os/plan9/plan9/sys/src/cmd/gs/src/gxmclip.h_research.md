# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxmclip.h

Mask clipping device structure and helper interface.

Key contents:
- Documents mask clipping use for ImageType 3 images and Patterns that do not fill their bounding box.
- Defines a small aligned tile clip buffer size.
- Defines `gx_device_mask_clip`, a forwarding device containing a mask bitmap, embedded memory device, phase, and aligned buffer.
- Declares the structure descriptor and `gx_mask_clip_initialize`.
- Defines `setup_mask_copy_mono`, a macro for copy-mono implementations to choose mask colors or fall back to default copy-mono behavior.

Notable dependencies:
- `gxclip.h` plus device/memory-device definitions supplied by including context.

Research notes:
- The structure is logically private but exposed so clients can allocate it directly.
- The phase is described as a device-space origin relative to the tile, opposite of graphics state phase semantics.
