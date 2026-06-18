# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsds.c

## Purpose
Implements custom stream filters used by PostScript/PDF image processing.

## Main Stream Families
- Bit-depth conversion:
  - `s_1_8_template`, `s_2_8_template`, `s_4_8_template`, `s_12_8_template`,
  - `s_8_1_template`, `s_8_2_template`, `s_8_4_template`.
- CMYK-to-RGB conversion:
  - `s_C2R_template`.
- Indexed conversion:
  - `s_IE_template`.
- Downsampling:
  - `s_Subsample_template`,
  - `s_Average_template`.
- Compression chooser:
  - `s_compr_chooser_template`.
- Image color/mask conversion:
  - `s__image_colors_template`.

## Key Behavior
- Expands packed 1/2/4/12-bit image samples to 8-bit values and reduces 8-bit samples back to packed 1/2/4-bit forms.
- Converts 8-bit CMYK image samples to RGB using Ghostscript color conversion and imager state.
- Builds an indexed palette on the fly, hashing component tuples into a caller-provided table.
- Implements simple subsampling and averaging downsampling streams.
- Implements a heuristic compression chooser that samples horizontal gradients/plateaus to classify likely photo versus line art.
- Implements image color conversion to:
  - 1-bit masks using `MaskColor` ranges,
  - device color components through color-space remapping.

## Dependencies
Uses Ghostscript stream infrastructure, color conversion, bitmap raster helpers, color spaces, device color remapping, and device client APIs.

## Research Notes
This is low-level streaming code. It is stateful and cursor-driven, designed to be inserted into psdf binary writer filter chains by `gdevpsdi.c`.
