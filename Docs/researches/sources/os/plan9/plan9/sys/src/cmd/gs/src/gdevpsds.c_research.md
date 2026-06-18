# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsds.c

## Purpose
Implements custom stream filters used by PostScript/PDF image processing.

## Main Stream Families
- Bit-depth conversion: `s_1_8_template`, `s_2_8_template`, `s_4_8_template`, `s_12_8_template`, `s_8_1_template`, `s_8_2_template`, `s_8_4_template`.
- CMYK-to-RGB conversion: `s_C2R_template`.
- Indexed conversion: `s_IE_template`.
- Downsampling: `s_Subsample_template`, `s_Average_template`.
- Compression chooser: `s_compr_chooser_template`.
- Image color/mask conversion: `s__image_colors_template`.

## Key Behavior
- Expands packed 1/2/4/12-bit image samples to 8-bit values and reduces 8-bit samples to packed 1/2/4-bit values.
- Converts 8-bit CMYK samples to RGB using Ghostscript color conversion and imager state.
- Builds an indexed palette on the fly by hashing component tuples into a caller-provided table.
- Implements center-point subsampling and averaging downsampling.
- Samples horizontal gradients and plateaus to heuristically classify image data as photo-like or line-art-like.
- Converts images either to 1-bit masks using `MaskColor` ranges or to device color components through color-space remapping.

## Dependencies
Uses Ghostscript stream cursor infrastructure, memory management, bitmap raster helpers, color conversion, color-space remapping, and device APIs.

## Research Notes
This is stateful cursor-driven streaming code. The apparent `p[1]` / `q[1]` access pattern is consistent with Ghostscript stream cursors, where `ptr` points before the next byte. Some in-code comments mark rough or incomplete behavior, including “WRONG” error returns, heuristic compression choice, and a “fixme” around input pointer handling in image-color conversion.
