# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrap.h

## Purpose
Defines trapping placement enums, trapping parameter structures, trapping zones, and the API for setting trap parameters from a parameter list.

## Public Surface
- `gs_trap_placement_t`: Center, Choke, Spread, Normal.
- `gs_trap_placement_names`: string names for enum parameter parsing.
- `gs_trap_params_t`: trapping parameters including black limits/width, enable flags, image trapping behavior, resolution, placement, sliding/step/color scaling limits, and trap width.
- `gs_trap_zone_t`: parameter set plus path pointer for a zone, marked subject to change.
- `gs_settrapparams(gs_trap_params_t *params, gs_param_list *list)`.

## Dependencies
Includes `gsparam.h` and forward-declares `gx_path`.

## Risks and Notes
- Several fields are commented out rather than represented (`ColorantZoneDetails`, `HalftoneName`), so this is a partial trapping model.
- `gs_trap_zone_t` is explicitly unstable.
