# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jccolor.c

Input color conversion module for JPEG compression.

Key behavior:
- Allocates and fills fixed-point RGB-to-YCbCr lookup tables for fast per-sample conversion.
- Converts interleaved application RGB rows into planar JPEG component buffers for YCbCr output.
- Reuses the Y portion of the RGB-to-YCbCr tables for RGB-to-grayscale conversion.
- Converts Adobe-style CMYK to YCCK by inverting C/M/Y into R/G/B, converting to YCbCr, and passing K through.
- Provides grayscale pass-through and generic null conversion for already matching color spaces.
- `jinit_color_converter` validates `input_components` against `in_color_space`, validates `num_components` against `jpeg_color_space`, and installs the appropriate `start_pass` and `color_convert` callbacks.

Dependencies:
- Uses IJG compressor state (`j_compress_ptr`), memory manager image pool allocation, `jpeg_color_converter`, `J_COLOR_SPACE`, `RGB_*` macros, and error macros from `jpeglib.h`.

Notable risks:
- Only a limited set of conversions is implemented; unsupported color-space pairs fail with `JERR_CONVERSION_NOTIMPL`.
- RGB pass-through is only allowed when `RGB_PIXELSIZE == 3`.
- The conversion tables are per-image allocations and are initialized only for conversions that set `rgb_ycc_start`.
