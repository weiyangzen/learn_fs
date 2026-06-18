# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdcolor.c

Purpose: output colorspace conversion for JPEG decompression.

Key structures and routines:
- `my_color_deconverter` extends `jpeg_color_deconverter` with cached YCbCr conversion tables.
- `build_ycc_rgb_table()` precomputes fixed-point Cb/Cr contribution tables for YCbCr to RGB/YCCK conversion.
- `ycc_rgb_convert()` converts planar YCbCr rows to interleaved RGB using `sample_range_limit`.
- `null_convert()` interleaves component planes without changing colorspace.
- `grayscale_convert()` copies luminance-only output, including YCbCr to grayscale by ignoring chroma.
- `gray_rgb_convert()` expands grayscale samples into RGB triples.
- `ycck_cmyk_convert()` handles Adobe-style YCCK to CMYK by converting YCbCr to inverted RGB-style CMY and passing K through.
- `jinit_color_deconverter()` validates component counts, selects conversion method, sets `out_color_components`, and clears `component_needed` for unused chroma in grayscale output.

Important behavior:
- Uses fixed-point scale `SCALEBITS = 16` to avoid floating point in hot loops.
- Range limiting is mandatory after lossy DCT reconstruction and color math.
- Supports grayscale, RGB, CMYK, YCbCr, YCCK, and null same-colorspace conversion; unsupported conversions call `JERR_CONVERSION_NOTIMPL`.
- If `quantize_colors` is enabled, final `output_components` is one colormapped component.

Dependencies:
- Requires `jinclude.h`, `jpeglib.h`, JPEG memory manager allocation, error macros, and RGB layout macros such as `RGB_RED`, `RGB_GREEN`, `RGB_BLUE`, `RGB_PIXELSIZE`.

Notes:
- This is image-decoder infrastructure embedded in the Plan 9 source tree via Ghostscript, not filesystem code.
