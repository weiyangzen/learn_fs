# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrap.c

## Purpose
Reads and validates trapping parameters from a Ghostscript parameter list into a `gs_trap_params_t` structure.

## Public Surface
- `gs_settrapparams(gs_trap_params_t *pparams, gs_param_list *plist)`: copies current params, applies any supplied parameter-list updates, validates ranges, and commits changes only if no error remains.

## Implementation
- `check_unit` accepts floats in `[0,1]`.
- `check_positive` accepts floats greater than zero.
- `trap_put_float_param` reads a float parameter, applies a validation callback, signals parameter errors, and preserves an accumulated error code.
- `gs_settrapparams` updates BlackColorLimit, BlackDensityLimit, BlackWidth, Enabled, ImageInternalTrapping, ImagemaskTrapping, ImageResolution, ImageToObjectTrapping, ImageTrapPlacement, SlidingTrapLimit, StepLimit, TrapColorScaling, and TrapWidth.
- Enum parsing for `ImageTrapPlacement` uses names from `gs_trap_placement_names`.
- `ImageResolution` is separately range-checked to be positive.

## Dependencies
Uses `gsparamx.h` parameter helpers, `gstrap.h` parameter definitions, and Ghostscript error codes.

## Risks and Notes
- This file sets parameters only; it does not implement trapping-zone rendering.
- Commit-on-success behavior avoids partially updating the caller's trap params when validation fails.
