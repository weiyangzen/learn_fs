# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparm4.h

## Role

`gsiparm4.h` defines Ghostscript ImageType 4 image parameters for masked-color images.

This is image parameter API infrastructure, not filesystem code.

## Main Declarations

- `gs_image4_t`: pixel-image common fields, `MaskColor_is_range`, and `MaskColor` array sized for exact values or ranges.
- `private_st_gs_image4()` GC descriptor macro.
- `gs_image4_t_init` initializer declaration.

## Important Contract

If `MaskColor_is_range` is false, the first N `MaskColor` entries are sample values. If true, the first `2*N` entries define sample ranges. The initializer defaults `MaskColor_is_range` to false.

## Notable Risks

Comments say the largest sample values currently supported by the library are 12 bits, though the design anticipates future DevicePixel images with larger samples.
