# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxipixel.c

Common Ghostscript ImageType 1 and 4 image enumerator initialization code.

Key behavior:
- Defines the GC descriptor for `gx_image_enum`, including special enumeration/relocation for cached device-color clue entries.
- `gx_image_enum_alloc` validates dimensions, bits/component, image format, optional subrectangle, and allocates the enumerator.
- `gx_image_enum_begin` computes the image-to-device matrix, initializes common plane metadata, validates imagemasks, configures decode/sample maps, normalizes image format, optimizes RasterOps, and allocates the unpack buffer.
- Determines image posture, extents, clipping flags, DDA origins, one-pixel-wide/high adjustment for old TeX/dvips line images, and renderer strategy.
- Chooses sample unpack procedures for 1/2/4/8/12/16-bit input, including interleaved variants.
- Sets up clipping forwarding devices and RasterOp texture devices when needed.
- `image_init_clues`, `image_init_colors`, and `image_init_map` initialize color clue caches and sample expansion/decode tables.
- `gx_image_scale_mask_colors` scales ImageType 4 mask color ranges into 8-bit sample space and handles Decode inversion.

Notable dependencies:
- Image class table from `gscdefs.h`.
- Graphics/image state from `gximage.h`, `gxistate.h`, and `gzstate.h`.
- Clipping and RasterOp devices from `gzcpath.h`, `gxdevmem.h`, and `gdevmrop.h`.

Research notes:
- This is the central setup path for ordinary and color-key masked image rendering.
- 12-bit and 16-bit support depends on external `sample_unpack_12_proc` and `sample_unpack_16_proc`; the stub files in this group set them to null.
- RasterOp rewrites can transform some 1-bit image operations into imagemask-style rendering for cheaper execution.
