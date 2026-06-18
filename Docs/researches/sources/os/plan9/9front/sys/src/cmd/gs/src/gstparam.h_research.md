# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstparam.h

Defines transparency parameter types shared by graphics state and PDF 1.4 compositor code.

Key definitions:
- `gs_blend_mode_t` enumerates supported blend modes from Compatible/Normal through Color, with `GS_BLEND_MODE_NAMES`.
- `gs_transparency_state_t` is the common stack-node header for transparency groups and masks.
- `gs_transparency_mask_t` is a refcounted cached mask header.
- `gs_transparency_group_params_t` carries optional blending color space plus Isolated and Knockout flags.
- `gs_transparency_mask_params_t` carries mask subtype, background components, gray background, transfer callback, and transfer function data.
- `gx_transparency_mask_params_t` is the post-command-list mask parameter form with sampled 256-byte transfer function.
- `gs_transparency_channel_selector_t` selects opacity or shape channel.

Research notes:
- Comments require `gs_trans_group_params_init` and `gs_trans_mask_params_init` to stay in sync with the parameter structures.
