# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhldevc.h

Purpose: declares helper structures and APIs for high-level device color preservation and comparison.

Key design constraints documented:
- Avoid changing the broad Ghostscript device interface.
- Avoid storing pointers to temporary or externally owned color-space/client-color objects.
- Preserve enough information to detect color-space and color changes in high-level devices.

Key type:
- `gx_hl_saved_color` stores `color_space_id`, `pattern_id`, `ccolor_valid`, a copied `gs_client_color`, and `gx_device_color_saved`.

APIs:
- Save/init/compare saved color records.
- Retrieve graphics-state pointer from imager state when possible.
- Query high-level color availability.
- Retrieve current color space and client color status.
- Query component counts and individual high-level component values.

Enums:
- `gx_hld_get_color_space_and_ccolor_status`: `non_pattern_color_space`, `pattern_color_sapce`, `use_process_color`.
- `gx_hld_get_color_component_status`: valid result or invalid color/component status.

Research notes:
- Header comments are important: they define the lifetime and pointer-safety model expected by high-level devices.
