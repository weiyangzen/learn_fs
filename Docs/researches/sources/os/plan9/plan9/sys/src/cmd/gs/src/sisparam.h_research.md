# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sisparam.h

Shared parameter definitions for Ghostscript image scaling streams.

Key contents:
- Defines maximum digital-filter support as `MAX_ISCALE_SUPPORT = 8`.
- Defines `stream_image_scale_params_t` with color count, input/output component bit depths, max component values, and input/output dimensions.
- Defines `stream_image_scale_state_common` and `stream_image_scale_state`.

Notable dependencies:
- Intended for stream filter implementations using `strimpl.h`.

Research notes:
- Supports 8- or 16-bit input/output components.
- The support cap bounds both runtime and temporary storage for scaling filters.
