# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsipar3x.h

Defines ImageType 3x, Ghostscript’s transparency-capable extension of ImageType 3.

Key definitions:
- `IMAGE3X_IMAGETYPE` is `103`.
- `gs_image3x_mask_t`: interleave type, optional Matte color, and mask dictionary.
- `gs_image3x_t`: pixel data dictionary plus opacity and shape masks.

Semantics:
- Supports `OpacityMaskDict` and/or `ShapeMaskDict`, with mask depths greater than one.
- `InterleaveType 3` supplies mask sources before pixel data, opacity before shape.
- `InterleaveType 2` is not allowed for this extension.
- MaskDict color spaces are ignored.
- `BitsPerComponent == 0` means a mask is not supplied.

Exports `gs_image3x_t_init`.
