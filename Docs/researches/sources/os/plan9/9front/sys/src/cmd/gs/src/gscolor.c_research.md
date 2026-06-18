# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor.c

## Role

`gscolor.c` implements core Ghostscript color and transfer-function operators for grayscale and RGB color, null color, transfer maps, and character-cache device color setup.

This is rendering/color graphics-state infrastructure, not filesystem code.

## Main Public Interfaces

- `gx_init_paint_1`
- `gx_init_paint_3`
- `gx_init_paint_4`
- `gx_restrict01_paint_1`
- `gx_restrict01_paint_3`
- `gx_restrict01_paint_4`
- `gx_no_adjust_color_count`
- `gs_setgray`
- `gs_setrgbcolor`
- `gs_setnullcolor`
- `gs_settransfer`
- `gs_settransfer_remap`
- `gs_currenttransfer`
- `gx_set_device_color_1`
- `load_transfer_map`

## Core Behavior

The file initializes paint component arrays for 1-, 3-, and 4-component spaces and clamps paint values into `[0,1]`.

`gs_setgray` and `gs_setrgbcolor` switch the graphics state to DeviceGray or DeviceRGB, set clamped paint values, clear pattern state, and invalidate cached device color.

`gs_setnullcolor` is disallowed inside `cachedevice`, otherwise it switches to harmless gray and marks device color null.

Transfer handling uses `gx_transfer_map` reference counting. `gs_settransfer_remap` unshares the gray transfer map, drops color transfer maps, assigns a new procedure, reloads the transfer cache if requested, updates effective transfer, and invalidates device color.

`load_transfer_map` samples either old-style function pointers or closure-style transfer callbacks into a fixed-size frac table.

## Dependencies

Uses Ghostscript color-space, device color, device, transfer-map, graphics state, and GC/refcount support.

## Notable Risks

- Transfer-map mutation relies on `rc_unshare_struct`; failure paths must restore reference counts.
- `gx_set_device_color_1` changes overprint and color-space state for character-cache rendering, so callers must use it only in the intended cache context.
