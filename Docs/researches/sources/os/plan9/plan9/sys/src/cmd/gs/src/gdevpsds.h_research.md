# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsds.h

## Purpose
Declares the custom image-processing stream states and templates implemented in `gdevpsds.c`.

## Main Definitions
- `stream_1248_state`: shared state for 1/2/4/12-bit to 8-bit expansion and 8-bit to 1/2/4-bit reduction.
- `stream_C2R_state`: CMYK-to-RGB conversion state carrying an imager-state pointer.
- `stream_IE_state`: IndexedEncode-like palette construction state with decode array, palette table, hash table, and bit packing state.
- `stream_Downsample_state_common`, `stream_Subsample_state`, `stream_Average_state`: downsampling states for subsample and average filters.
- `stream_compr_chooser_state`: heuristic image classifier state for compression selection.
- `stream_image_colors_state`: color-to-mask or color-space-to-device conversion state.

## Key API
- Declares stream templates for bit-depth conversion, CMYK-to-RGB, indexed conversion, subsampling, averaging, compression choosing, and image color conversion.
- Exposes initialization and setup helpers:
  - `s_1248_init`,
  - `s_C2R_init`,
  - `s_Downsample_size_out`,
  - `s_compr_chooser_set_dimensions`,
  - `s_compr_chooser__get_choice`,
  - `s_image_colors_set_dimensions`,
  - `s_image_colors_set_mask_colors`,
  - `s_image_colors_set_color_space`.

## Dependencies
Includes stream implementation headers and image parameter definitions; forward-declares `gx_device`.

## Research Notes
The header exposes both `s_image_colors_template` and `s__image_colors_template`, while the implementation defines `s__image_colors_template`. The single-underscore declaration appears stale or unused in this source snapshot.
