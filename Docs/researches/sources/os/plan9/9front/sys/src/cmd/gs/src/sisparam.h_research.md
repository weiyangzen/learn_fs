# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sisparam.h

Defines shared image scaling stream parameters.

Key points:
- Describes common input/output parameters used by image scaling streams.
- Defines `MAX_ISCALE_SUPPORT` as 8, bounding filter support and temporary storage.
- `stream_image_scale_params_t` includes colors, input/output bits per component, max component values, and input/output width/height.
- `stream_image_scale_state_common` embeds standard stream state plus the scaling parameter structure.

Research relevance:
- This is the common parameter contract for `siinterp.c` and `siscale.c`.
