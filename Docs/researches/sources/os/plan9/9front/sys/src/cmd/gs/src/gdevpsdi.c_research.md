# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdi.c

## Purpose
Builds image compression, downsampling, color-conversion, and chooser filter pipelines for PostScript/PDF writers.

## Key Behavior
- `pixel_resize` inserts streams converting between packed 1/2/4/12-bit samples and 8-bit samples.
- `choose_DCT_params` heuristically adjusts JPEG/DCT parameters based on whether a color space behaves like RGB, Lab, or unknown.
- `setup_image_compression` selects and configures compression filters:
  - DCT/JPEG,
  - CCITTFax,
  - LZW,
  - Flate/zlib,
  - PNG predictor for suitable lossless Level 3 output.
- `do_downsample` and `setup_downsampling` add subsample or average downsampling streams and update image dimensions/matrix metadata.
- `psdf_setup_image_filters` is the main public pipeline builder:
  - chooses mono/gray/color image parameter sets,
  - computes effective image resolution from image matrix and CTM,
  - applies downsampling when thresholds are met,
  - optionally converts CMYK images to RGB,
  - applies depth conversion and compression in stream-order.
- `psdf_setup_lossless_filters` creates a temporary psdf device configured for lossless Flate output.
- Exposes helpers for compression chooser, image-to-mask conversion, and device color conversion filters.

## Dependencies
Relies on stream templates from `gdevpsds.c`, Ghostscript color-space APIs, JPEG/DCT, CCITT Fax, LZW, PNG predictor, RunLength, and zlib stream templates.

## Research Notes
This file is pipeline orchestration code. It does not implement low-level stream algorithms itself; those live mostly in `gdevpsds.c`. The code mutates image descriptors as filters change image size, bit depth, or color space.
