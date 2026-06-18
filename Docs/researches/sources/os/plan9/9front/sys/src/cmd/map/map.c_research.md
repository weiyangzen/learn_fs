# File Research: sources/os/plan9/9front/sys/src/cmd/map/map.c

Implements the `map` command front end: parses projection/options, sets geographic limits/windows/orientation, computes plot scaling, draws grid/borders, reads map datasets, and plots tracks/symbols through the selected projection.

Key behavior:
- Selects a projection from the global `index[]` table, validates projection parameters, and installs projection/cut/limb handlers.
- Handles options for map files, tracks, clipping polygons, grid/window/limit bounds, orientation, colors/styles, reverse x-axis, thinning, and symbol files.
- Reads map data through `.x` patch indexes and packed absolute/differential coordinate records, skipping unseen 10-degree patches.
- Normalizes geographic points, applies windows/limits/cut handling, projects to x/y, clips to optional convex polygon, scales to plot coordinates, and emits `iplot` drawing commands.
- Draws projection limbs, borders, latitude/longitude grids, tracks, text labels, and named symbols.

Important dependencies: `map.h`, `iplot.h`, projection functions from `libmap`, Plan 9 libc/stdio, global `index[]`, `colorcode`, and plot primitives like `openpl`, `vec`, `point`, `text`.

Notable risks:
- Heavy global state means option ordering and projection state interact closely.
- `getshort()` assumes 16-bit little-endian encoded map records and aborts if `short` is not 2 bytes.
- Cut logic and line-length suppression prevent false lines across map discontinuities; small changes can create visual artifacts.
