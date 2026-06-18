# File Research: sources/os/plan9/plan9/sys/src/cmd/map/map.c

Main command driver for Plan 9 `map`.

Responsibilities:
- Parses projection name, projection parameters, and rendering options.
- Initializes projection function, cut handler, limb iterator, orientation, limits, clipping polygon, scale, and plot viewport.
- Draws grid, border/limb, map files, tracks, and symbols through `iplot`.
- Reads packed map data using `.x` index sidecar files and binary coordinate deltas.
- Handles map cuts, visible windows, clipping, and projection return-code recoding.

Important flow:
- `main()` resolves projection from external `index[]`, parses options such as `-m`, `-g`, `-o`, `-l`, `-k`, `-w`, `-p`, `-v`, `-C`, then computes bounds by sampling projected points.
- `fixproj()` recodes projection return values from `-1/0/1` into renderer semantics.
- `normproj()` converts lat/lon, normalizes orientation, checks window, and projects.
- `plotpt()` checks geographic limits, normalizes, handles cuts, and calls `doproj()`.
- `doproj()` applies projection, optional reflection, polygon clipping, centering, rotation, scaling, and integer conversion.
- `getdata()` reads indexed map patches in absolute or differential encoding.
- `dogrid()`, `dobounds()`, `dolimb()` draw graticules, boundaries, and projection limbs.

Cut handling:
- `picut()` and `ckcut()` handle longitude-PI seam crossing.
- `duple()` redraws near-cut segments on both sheets.
- `realcut()` disables cuts when the window does not actually include the seam.

Notable data:
- Global map file list, track list, color/style state, geographic limits/window, clipping polygon equations, scaling/centering state.
- `patch[18][36]` indexes 10-degree tiles.

Behavior notes:
- Uses Plan 9 plotting primitives from `iplot.h`.
- Assumes `sizeof(short) == 2` for binary map data.
- Long segment suppression prevents drawing lines across projection cuts.
