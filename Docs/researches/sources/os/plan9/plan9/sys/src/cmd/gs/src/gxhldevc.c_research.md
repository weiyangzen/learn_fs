# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhldevc.c

Purpose: implements helper routines for high-level devices to save, compare, and query color-space-aware device colors without storing unsafe pointers into transient graphics-state objects.

Main functions:
- `gx_hld_saved_color_init`: clears a saved-color record, marks ids as `gs_no_id`, and saves a null device color.
- `gx_hld_get_gstate_ptr`: verifies an imager state is actually a `gs_state` via Ghostscript object type metadata.
- `gx_hld_save_color`: saves color space id, pattern id when applicable, client color component values, and device-color-specific saved data.
- `gx_hld_saved_color_equal`: compares two full saved-color structs with `memcmp`.
- `gx_hld_saved_color_same_cspace`: compares ids and validity metadata for color-space sameness.
- `gx_hld_is_hl_color_available`: checks for graphics state, device color, and valid client color.
- `gx_hld_get_color_space_and_ccolor`: returns current color space and client color pointers when valid, distinguishing pattern and non-pattern color-space cases.
- `gx_hld_get_number_color_components`: returns component count from the current graphics-state color space.
- `gx_hld_get_color_component`: returns a requested high-level color component.

Dependencies:
- Uses graphics state, color space, device color, pattern color, and Type 2 pattern headers.
- Relies on `gx_device_color.type->save_dc` for polymorphic device color saving.

Research notes:
- `pattern_color_sapce` is misspelled in the enum and implementation, so callers must use the existing spelling.
- `gx_hld_saved_color_same_cspace` repeats a color_space_id check; harmless but redundant.
