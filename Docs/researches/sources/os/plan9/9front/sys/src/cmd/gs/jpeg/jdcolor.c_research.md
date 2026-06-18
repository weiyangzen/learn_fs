# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdcolor.c

Output colorspace conversion for decompression.

Key points:
- Builds fixed-point lookup tables for YCbCr/YCCK conversion to avoid inner-loop multiplications.
- Implements YCbCr-to-RGB, no-op planar-to-interleaved conversion, grayscale extraction, grayscale-to-RGB expansion, and Adobe YCCK-to-CMYK conversion.
- Uses `sample_range_limit` for RGB/YCCK outputs because DCT losses can push computed values outside sample range.
- Validates `jpeg_color_space` against `num_components` and selects conversion based on requested `out_color_space`.
- Marks chroma components unneeded when output is grayscale from grayscale or YCbCr, allowing earlier stages to avoid work.
- Sets `out_color_components` and final `output_components`, with color quantization reducing output to one colormapped component.

Dependencies and interactions:
- Called after upsampling unless merged upsample/color conversion is selected.
- Shares conversion constants and layout macros with `jdmerge.c` and public RGB configuration.

Risk notes:
- Unsupported conversions fail at initialization with `JERR_CONVERSION_NOTIMPL`.
- RGB no-op conversion is only used when `RGB_PIXELSIZE == 3`; other RGB layouts require explicit support.
- Color-space inference happens earlier in `jdapimin.c`, so this module depends on those defaults or application overrides being coherent.
