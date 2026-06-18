# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhldevc.h

## Role

`gxhldevc.h` declares the high-level device color save/compare helper API used by Ghostscript devices that need color-space-aware output without changing the wider device interface.

This is graphics device/color infrastructure, not filesystem code.

## Design Intent

- Avoid broad changes to Ghostscript's long-standing device interface.
- Avoid saving pointers to graphics-state color space structures that may be temporary, stack-based, or freed outside the device.
- Save enough stable identifiers and value data to detect high-level color/color-space changes across device operations.

## Main Types

- `gx_hl_saved_color` stores:
  - `color_space_id`
  - `pattern_id`
  - `ccolor_valid`
  - `gs_client_color ccolor`
  - `gx_device_color_saved saved_dev_color`
- `gx_hld_get_color_space_and_ccolor_status` has statuses for non-pattern color space, pattern color space, and process-color fallback.
- `gx_hld_get_color_component_status` reports valid component, invalid color info, or invalid component request.

## Public Interface

- Initialization/comparison: `gx_hld_saved_color_init`, `gx_hld_saved_color_equal`, `gx_hld_saved_color_same_cspace`.
- Context lookup: `gx_hld_get_gstate_ptr`.
- Save/query helpers: `gx_hld_save_color`, `gx_hld_is_hl_color_available`, `gx_hld_get_color_space_and_ccolor`, `gx_hld_get_number_color_components`, `gx_hld_get_color_component`.

## Notable Risks

- The header contract for `gx_hld_get_color_space_and_ccolor` should be checked against implementation behavior before relying on `ppcc == NULL` for non-pattern colors.
- The status name `pattern_color_sapce` is misspelled and therefore part of the compiled API.
- `gx_hl_saved_color` comparison depends on unused fields being zeroed before use.
