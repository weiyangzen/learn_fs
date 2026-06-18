# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor1.c

## Role

`gscolor1.c` implements Ghostscript Level 1 extended color operators: CMYK color, black generation, undercolor removal, and color transfer functions.

This is rendering/color graphics-state infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_setcmykcolor`
- `gs_setblackgeneration`
- `gs_setblackgeneration_remap`
- `gs_currentblackgeneration`
- `gs_setundercolorremoval`
- `gs_setundercolorremoval_remap`
- `gs_currentundercolorremoval`
- `gs_setcolortransfer`
- `gs_setcolortransfer_remap`
- `gs_currentcolortransfer`

## Core Behavior

`gs_setcmykcolor` switches the current color space to DeviceCMYK, clamps all four components, clears pattern state, and invalidates device color.

Black generation and undercolor removal setters unshare the corresponding transfer map, assign the new procedure, stamp a new ID, optionally sample it into the cached transfer map, and invalidate device color.

`gs_setcolortransfer_remap` unshares gray/red/green/blue transfer maps, assigns new transfer procedures and IDs, records device component numbers for Red/Green/Blue/Gray halftone transfer lookup, reloads maps if requested, updates effective transfer, and invalidates device color.

## Dependencies

Uses `load_transfer_map` from `gscolor.c`, effective transfer setup from halftone code, color-space/device-color internals, and halftone component-name lookup.

## Notable Risks

- The `setcolortransfer` failure path restores some old map pointers by `rc_assign`, but the sequence is delicate because multiple unshare operations can fail at different points.
- Device component-name lookup occurs at setter time and depends on the current device.
