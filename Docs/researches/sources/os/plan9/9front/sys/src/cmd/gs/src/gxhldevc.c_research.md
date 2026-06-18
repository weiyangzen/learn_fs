# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhldevc.c

## Role

`gxhldevc.c` implements helper procedures for high-level devices that need to save, compare, and recover color-space/client-color information associated with a Ghostscript `gx_device_color`.

This is graphics device/color infrastructure, not filesystem code.

## Main Functions

- `gx_hld_saved_color_init`: clears a saved color, sets color-space and pattern ids to `gs_no_id`, and saves a null device color.
- `gx_hld_get_gstate_ptr`: verifies that an imager state pointer is actually a `gs_state` object using Ghostscript structure type metadata.
- `gx_hld_save_color`: saves color space id, device color-specific state, client color paint values, and pattern id when available.
- `gx_hld_saved_color_equal`: compares complete saved-color structures with `memcmp`.
- `gx_hld_saved_color_same_cspace`: compares color-space id, pattern id, and `ccolor_valid`.
- `gx_hld_is_hl_color_available`: checks whether a graphics state and valid client color are available.
- `gx_hld_get_color_space_and_ccolor`: returns current color space and client color pointers plus pattern/non-pattern/process-color status.
- `gx_hld_get_number_color_components`: returns the component count for the current graphics state's color space, normalizing negative values.
- `gx_hld_get_color_component`: returns an individual high-level color component when valid.

## Dependencies And Integration

- Uses `gzstate.h`, `gscspace.h`, `gxcspace.h`, `gxdcolor`-related types from `gxhldevc.h`, pattern device color types, and Ghostscript structure descriptors.
- Integrates with `gx_device_color` polymorphic methods through `pdevc->type->save_dc`.
- Uses color-space ids and pattern ids rather than saving pointers that could become dangling.

## Notable Risks

- `gx_hld_save_color` clears `psc` and copies `pdevc->ccolor.paint.values`, but does not visibly assign `psc->ccolor_valid`; this may be intentional reliance on zeroed state or a missing field copy, and it affects `gx_hld_saved_color_same_cspace`.
- `gx_hld_saved_color_same_cspace` checks `color_space_id` twice.
- The implementation of `gx_hld_get_color_space_and_ccolor` returns `ppcc = &pdevc->ccolor` for non-pattern colors, while the header comment says the client color pointer will be `NULL` for the non-pattern case.
- Several public enum/status names have typos (`pattern_color_sapce`, comments such as "availavble"), which can leak into API use.
