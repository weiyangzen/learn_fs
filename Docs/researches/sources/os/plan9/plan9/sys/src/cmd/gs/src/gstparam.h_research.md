# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstparam.h

## Purpose
Defines shared transparency parameter types: blend modes, transparency stack state headers, cached mask headers, group parameters, mask parameters, serialized mask parameters, and opacity/shape channel selection.

## Public Surface
- `gs_blend_mode_t`: PDF-style blend modes from Compatible/Normal through Color, with `MAX_BLEND_MODE`.
- `GS_BLEND_MODE_NAMES`: string names matching the enum.
- `gs_transparency_state_type_t`: group or mask state.
- `gs_transparency_state_t`: common saved/type stack node.
- `gs_transparency_mask_t`: reference-counted cached mask common header.
- `gs_transparency_group_params_t`: group `ColorSpace`, `Isolated`, and `Knockout`.
- `gs_transparency_mask_subtype_t`: Alpha or Luminosity.
- `gs_transparency_mask_params_t`: mask subtype, background components/colors, gray background, transfer function callback, and transfer function data.
- `gx_transparency_mask_params_t`: post-command-list representation with sampled 256-entry transfer function.
- `gs_transparency_channel_selector_t`: opacity or shape.

## Dependencies
Includes client color max component definitions and reference-count headers. Forward-declares color space and function types.

## Risks and Notes
- Comments require updating initialization routines if group or mask parameter structures change.
- `MASK_TRANSFER_FUNCTION_SIZE` fixes transfer-function sampling at 256 entries for command-list/post-clist mask parameters.
