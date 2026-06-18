# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor.c

## Purpose
Basic Ghostscript color and transfer-function operators.

## Key Behavior
- Defines GC descriptors for client colors and transfer maps.
- Provides paint initialization helpers for 1, 3, and 4 component spaces.
- Provides `[0..1]` restriction helpers for 1, 3, and 4 component paint values.
- Implements `gs_setgray`, `gs_setrgbcolor`, and `gs_setnullcolor`.
- Implements `gs_settransfer`, `gs_settransfer_remap`, and `gs_currenttransfer`.
- Implements `gx_set_device_color_1` for character-cache rendering.
- Exports `load_transfer_map`, which samples either old-style transfer procs or closure-based maps into `frac` tables.

## Important Details
- `setgray` and `setrgbcolor` temporarily initialize a local device color space and call `gs_setcolorspace`.
- `setnullcolor` is forbidden inside `cachedevice`.
- `gs_settransfer_remap` unshares only the gray map and clears red/green/blue maps, restoring reference counts on allocation failure.
- Transfer values are clamped to a caller-provided minimum and to `1.0`.

## Dependencies
Uses color-space internals, device-color conversion, transfer maps, graphics-state internals, and halftone transfer recalculation.

## Research Notes
This is the base color operator layer; CMYK and multi-channel transfer functions are in `gscolor1.c`.
