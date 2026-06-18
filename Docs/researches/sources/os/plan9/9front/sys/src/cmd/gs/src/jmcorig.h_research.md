# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jmcorig.h

Original IJG `jmorecfg.h` configuration body for JPEG library data types and compile-time feature switches. Ghostscript keeps this as the upstream baseline and then wraps it with `jmorecf0.h`/`jmorecfg.h` to disable or adjust selected features.

Core image/data type settings:
- `BITS_IN_JSAMPLE` is set to `8`, selecting 8-bit JPEG sample values.
- `MAX_COMPONENTS` is set to `10`.
- `JSAMPLE`, `JOCTET`, `UINT8`, `UINT16`, `INT16`, `INT32`, and `JDIMENSION` are selected from C scalar types based on `HAVE_UNSIGNED_CHAR`, `CHAR_IS_UNSIGNED`, and `HAVE_UNSIGNED_SHORT`.
- `JCOEF` is `short`, `JPEG_MAX_DIMENSION` is `65500L`, and `GETJSAMPLE`/`GETJOCTET` mask signed chars when needed.

It defines IJG linkage and declaration macros:
- `METHODDEF`, `LOCAL`, `GLOBAL`, and `EXTERN` for static/global linkage.
- `JMETHOD` for function-pointer methods with or without prototypes.
- `FAR` for old 80x86 far-pointer builds, controlled by `NEED_FAR_POINTERS`.
- `boolean`, `FALSE`, and `TRUE` unless already supplied by the including application.

When `JPEG_INTERNALS` or `JPEG_INTERNAL_OPTIONS` is defined, it exposes library feature switches. The baseline enables integer and floating DCT variants, progressive and multiscanner encoder/decoder support, entropy optimization, input smoothing, marker saving, block smoothing, IDCT scaling, upsample merging, and one/two-pass quantization. Arithmetic coding and upsample-stage scaling are disabled. RGB scanline ordering is standard `R,G,B` with `RGB_PIXELSIZE=3`.

Speed/portability knobs include `INLINE`, `MULTIPLIER`, and `FAST_FLOAT`, with GCC inline support and `float` selected when prototypes are available.

Ghostscript's wrapper later changes this baseline by undefining several encoder and decoder options and by increasing `D_MAX_BLOCKS_IN_MCU` for Adobe-compatible DCT filter input.

Filesystem relevance: none directly. It is codec compile-time configuration for the Ghostscript userland application.
