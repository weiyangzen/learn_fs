# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jccolor.c

Input color conversion module for compression.

Key points:
- Allocates a color converter with optional precomputed RGB-to-YCbCr tables.
- `rgb_ycc_start` builds fixed-point tables for CCIR 601-derived RGB to YCbCr conversion, including chroma offsets and rounding.
- Implements `rgb_ycc_convert`, `rgb_gray_convert`, `cmyk_ycck_convert`, `grayscale_convert`, and `null_convert`.
- Converts application interleaved input rows into libjpeg’s internal planar component buffers.
- `jinit_color_converter` validates `input_components` against `in_color_space`, validates `num_components` against `jpeg_color_space`, selects a conversion function, and installs `rgb_ycc_start` only when table-backed conversion is needed.

Dependencies and interactions:
- Called by `jcprepct.c` before downsampling.
- Relies on `RGB_RED`, `RGB_GREEN`, `RGB_BLUE`, and `RGB_PIXELSIZE` configuration from the public headers.

Risk notes:
- Only selected conversions are implemented: RGB to YCbCr/grayscale, CMYK to YCCK, direct pass-through, and grayscale extraction.
- Unsupported colorspace combinations fail at initialization.
- Conversion math assumes samples are in the configured `0..MAXJSAMPLE` range.
