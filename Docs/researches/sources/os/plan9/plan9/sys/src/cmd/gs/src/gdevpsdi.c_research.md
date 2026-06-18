# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdi.c

## Purpose
Builds image compression, downsampling, bit-depth conversion, and color-conversion filter chains for PostScript/PDF output devices.

## Key Behavior
- Adds pixel resize filters between 1/2/4/12-bit samples and 8-bit samples using stream templates from `gdevpsds.c`.
- Chooses DCT/JPEG parameters heuristically based on whether a 3-component color space behaves like RGB, Lab, or an unknown space.
- Sets up image compression:
  - DCTEncode for suitable 8-bit non-indexed data,
  - CCITTFaxEncode for mono defaults,
  - LZWEncode or FlateEncode depending on version and settings,
  - optional PNG predictor for LanguageLevel 3 lossless streams.
- Implements downsampling filter setup with `Subsample` or `Average`; `Bicubic` is treated as average.
- Computes effective image resolution from image matrix, CTM, and device resolution to decide whether downsampling should apply.
- Supports optional CMYK-to-RGB conversion through `s_C2R_template` when `ConvertCMYKImagesToRGB` is enabled.
- Provides lossless-only filter setup by copying the psdf device and overriding image parameters.
- Creates compression chooser, image-to-mask, and image-color conversion filter chains.

## Dependencies
Uses `gdevpsdf.h`, `gdevpsds.h`, memory device helpers, color-space APIs, DCT/JPEG, CCITT Fax, LZW, RunLength, PNG predictor, and zlib stream templates.

## Research Notes
The filter pipeline is built back-to-front and may mutate `gs_pixel_image_t` metadata such as dimensions, bits per component, image matrix, decode array, and color space. Several comments mark incomplete behavior, including no true antialiasing in downsampling and image-color conversion being a limited/stub conversion path.
