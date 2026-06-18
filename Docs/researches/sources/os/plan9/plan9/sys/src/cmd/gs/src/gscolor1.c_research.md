# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor1.c

## Purpose
Implements Level 1 extended color operators: CMYK color setting, black generation, undercolor removal, and color transfer functions.

## Key Behavior
- `gs_setcmykcolor` switches to DeviceCMYK, clamps component values, clears patterns, and invalidates device color.
- `gs_setblackgeneration_remap` unshares and updates the black-generation transfer map.
- `gs_setundercolorremoval_remap` unshares and updates the undercolor-removal transfer map, sampling with minimum `-1.0`.
- `gs_setcolortransfer_remap` unshares gray/red/green/blue transfer maps, assigns new IDs, updates color-component numbers, optionally samples all maps, and updates effective transfer.
- Provides current-value accessors for black generation, undercolor removal, and color transfer.

## Important Details
- `gs_setcolortransfer_remap` stores a full old transfer structure and restores partially changed references on allocation failure.
- Component names are resolved through `gs_color_name_component_number` for Red, Green, Blue, and Gray, which supports device/component-aware halftone behavior.
- Remap-disabled variants are used by the interpreter when delayed remapping is required.

## Dependencies
Uses `load_transfer_map` from `gscolor.c`, graphics-state internals, halftone types, transfer maps, color-space setup, and device component lookup.

## Research Notes
This file extends `gscolor.c`; it does not define current CMYK color retrieval despite the header declaration.
