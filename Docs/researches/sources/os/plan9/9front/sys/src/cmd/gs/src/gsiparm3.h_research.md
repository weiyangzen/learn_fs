# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiparm3.h

## Role

`gsiparm3.h` defines Ghostscript ImageType 3 parameters for images with masks.

This is image parameter API infrastructure, not filesystem code.

## Main Declarations

- `gs_image3_interleave_type_t`: chunky, interleaved scan lines, or separate mask source.
- `gs_image3_t`: pixel-image DataDict, `InterleaveType`, and `MaskDict`.
- `private_st_gs_image3()` GC descriptor macro.
- `gs_image3_t_init` initializer declaration.

## Important Contract

For InterleaveTypes 2 and 3, the client is responsible for providing mask data before the image data it masks. For InterleaveType 3, mask data is an additional data source before pixel data.

## Notable Risks

The header states that the implementation does not currently check the mask-before-pixel ordering requirement.
