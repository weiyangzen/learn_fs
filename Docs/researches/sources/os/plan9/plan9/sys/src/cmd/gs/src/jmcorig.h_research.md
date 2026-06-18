# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jmcorig.h

## Identity

- Lines/bytes: 363 lines, 12,458 bytes.
- SHA-256: `262138c3433e81e84e9f6811b38b5dc63e6f161e9b952afb0ff61b4a39b697a9`.
- Role: original IJG `jmorecfg.h` configuration copied as `jmcorig.h`.

## Contents

This is the IJG v6-era secondary configuration header. It defines:

- JPEG sample precision: `BITS_IN_JSAMPLE 8`.
- Maximum image components: `MAX_COMPONENTS 10`.
- Core JPEG data types: `JSAMPLE`, `JCOEF`, `JOCTET`, `UINT8`, `UINT16`, `INT16`, `INT32`, `JDIMENSION`.
- JPEG dimension limit: `JPEG_MAX_DIMENSION 65500L`.
- Linkage/function declaration macros: `METHODDEF`, `LOCAL`, `GLOBAL`, `EXTERN`, `JMETHOD`, `FAR`.
- Boolean type and `FALSE`/`TRUE` when not already supplied.
- Optional internal capabilities when `JPEG_INTERNALS` or `JPEG_INTERNAL_OPTIONS` is defined.

## JPEG Capabilities

Enabled in the original configuration:

- DCT methods: slow integer, fast integer, and floating point.
- Encoder: multi-scan, progressive, entropy optimization, input smoothing.
- Decoder: multi-scan, progressive, marker saving, block smoothing, IDCT scaling, upsample merging, one-pass and two-pass quantization.
- RGB memory layout: `RGB_RED 0`, `RGB_GREEN 1`, `RGB_BLUE 2`, `RGB_PIXELSIZE 3`.

Disabled:

- Arithmetic coding for both compression and decompression.
- Upsample-stage scaling.

## Dependencies

- Consumed by `jmorecf0.h` and `jmorecfg.h`.
- Relies on symbols from `jconfig.h`, such as `HAVE_UNSIGNED_CHAR`, `HAVE_UNSIGNED_SHORT`, `CHAR_IS_UNSIGNED`, `HAVE_PROTOTYPES`, and `NEED_FAR_POINTERS`.

## Behavior And Integration

- Establishes public ABI-visible IJG types used by `jpeglib.h`.
- Acts as the baseline before Ghostscript’s wrapper disables unneeded features.

## Research Notes

- This is third-party IJG configuration preserved inside Ghostscript.
- Ghostscript keeps it separate as `jmcorig.h` so its wrapper can include the original and then override selected features.
