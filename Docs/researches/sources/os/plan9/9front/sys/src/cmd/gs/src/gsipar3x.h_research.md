# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsipar3x.h

## Role

`gsipar3x.h` defines Ghostscript's extended ImageType 3x parameters for transparency-capable images with opacity and shape masks.

This is image parameter API infrastructure, not filesystem code.

## Main Declarations

- `IMAGE3X_IMAGETYPE` constant set to `103`.
- `gs_image3x_mask_t`: interleave type, optional matte color, and mask data dictionary.
- `gs_image3x_t`: pixel-image DataDict plus `Opacity` and `Shape` mask dictionaries.
- `private_st_gs_image3x()` GC descriptor macro.
- `gs_image3x_t_init` initializer declaration.

## Important Contract

For `InterleaveType == 3`, mask data sources precede pixel data sources, with opacity before shape. InterleaveType 2 is not allowed for this image type. MaskDict color spaces are ignored, and `BitsPerComponent == 0` means a mask is not supplied.

## Notable Risks

The header says the implementation does not currently check that clients always provide mask data before the pixel data it masks.
