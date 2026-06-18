# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxipixel.c

Common Ghostscript ImageType 1 and 4 image enumerator initialization code.

Key behavior:
- Defines the GC descriptor for `gx_image_enum`, including special enumeration/relocation of cached device-color clue entries.
- `gx_image_enum_alloc` validates image dimensions, bits-per-component, image format, and optional subrectangle, then allocates and initializes the source rectangle.
- `gx_image_enum_begin` computes the image-to-device matrix, initializes plane metadata, validates image masks, configures decode/sample maps, normalizes image format, optimizes RasterOps, and allocates the unpack buffer.
- Determines image posture, extents, clipping state, DDA row/strip/pixel origins, and special one-pixel-wide/high adjustment for old TeX/dvips line images.
- Chooses an unpack procedure for 1/2/4/8/12/16-bit input, with interleaved variants when necessary.
- Selects an image class renderer from the global image class table.
- Sets up clip forwarding devices and RasterOp texture devices when needed.
- `image_init_clues`, `image_init_colors`, and `image_init_map` initialize device-color caches and sample decode expansion tables.
- `gx_image_scale_mask_colors` scales ImageType 4 mask-color ranges to 8-bit sample values and accounts for Decode inversion.

Notable dependencies:
- Image class table from `gscdefs.h`.
- Graphics/image state from `gximage.h`, `gxistate.h`, `gzstate.h`.
- Clipping, memory, and RasterOp devices from `gzcpath.h`, `gxdevmem.h`, and `gdevmrop.h`.

Research notes:
- This is the central setup path for ordinary and color-key masked images.
- 12-bit and 16-bit handling depends on external `sample_unpack_12_proc` and `sample_unpack_16_proc`; the stub files in this group set them to null.
- RasterOp rewrites can transform some 1-bit image operations into imagemask-style rendering for cheaper execution.
