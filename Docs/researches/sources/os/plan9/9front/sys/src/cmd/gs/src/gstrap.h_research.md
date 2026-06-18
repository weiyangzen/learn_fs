# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrap.h

Defines trapping parameter and zone structures.

Key definitions:
- `gs_trap_placement_t` enumerates Center, Choke, Spread, and Normal placement with matching name macro.
- `gs_trap_params_t` contains black/color limits, widths, enabled flags, image trapping flags, image resolution, image trap placement, sliding/step/color-scaling limits, and trap width.
- `gs_trap_zone_t` pairs trapping params with a path pointer and is marked subject to change.

Public API:
- `gs_settrapparams` reads/validates parameters from a `gs_param_list`.

Research notes:
- Several possible parameters are commented out, including colorant zone details and halftone name.
