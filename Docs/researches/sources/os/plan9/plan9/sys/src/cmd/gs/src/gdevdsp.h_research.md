# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsp.h

Public ABI header for the Ghostscript display callback device.

Key contents:
- Documents API order: `gsapi_new_instance`, `gsapi_set_display_callback`, `gsapi_init_with_args`.
- Defines display format bitfields for color model, alpha/unused component layout, bit depth, endian/channel order, first row direction, 555/565 packing, and row alignment.
- Defines `display_callback` version 2, adding `display_separation`.
- Keeps `display_callback_v1_s` for backward compatibility.

Risks / notes:
- ABI depends on exact structure size/version checks in `gdevdsp.c`.
- `DisplayHandle` carries caller pointer-like data as a string/number.
