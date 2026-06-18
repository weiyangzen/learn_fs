# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsds.h

## Purpose
Declares the image-processing stream states and templates implemented in `gdevpsds.c`.

## Main Declarations
- `stream_1248_state`: row-aware state for bit-depth expansion/reduction.
- `stream_C2R_state`: CMYK-to-RGB conversion state with imager-state pointer.
- `stream_IE_state`: indexed image conversion state with decode data, palette table, hash table, and bit packing state.
- `stream_Downsample_state`, `stream_Subsample_state`, `stream_Average_state`: shared and concrete downsampling states.
- `stream_compr_chooser_state`: compression decision heuristic state.
- `stream_image_colors_state`: mask/device-color conversion state for image samples.

## Key Exports
- Stream templates for depth conversion, color conversion, indexed conversion, downsampling, compression choice, and image color conversion.
- Initialization helpers such as `s_1248_init`, `s_C2R_init`, and `s_compr_chooser_set_dimensions`.
- Dimension and conversion configuration helpers for image color streams.

## Dependencies
Includes stream implementation support and image parameter types.

## Research Notes
This header is the interface layer between image filter pipeline construction in `gdevpsdi.c` and the concrete cursor-based stream implementations in `gdevpsds.c`.
