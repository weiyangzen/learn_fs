# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdcolor.h

This header defines the device color representation used by Ghostscript drivers and painting code.

It exposes read-only and read/write macros for:
- Pure device colors.
- Binary halftones.
- Colored halftones.
- Pattern colors and masks.
- Halftone/pattern phase handling.
- Null and unset colors.

The core structure `gx_device_color_s` stores:
- A device color type pointer.
- A union for pure colors, binary halftone state, colored halftone state, Well-Tempered Screening state, or pattern tile state.
- Phase.
- `ccolor_valid` plus original `gs_client_color`.
- Pattern mask metadata and cached tile references.

It also defines `gx_device_color_saved_s`, a compact saved-color representation used by command-list and vector devices to compare or avoid resending colors without retaining unsafe pointers to reference-counted halftones.

Important design constraint: device colors may reference halftones, but those references are not counted. Saved colors intentionally avoid holding such pointers because command-list data may outlive the current imager-state halftone.

Integration is broad: this header is used by color mapping, painting, halftone loading, pattern rendering, command-list writing, and overprint code in `gscspace.c`.
