# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcie.c

Implements Level 2 CIE color-space operators and CIE procedure-cache setup.

Key behavior:
- Provides dictionary parameter helpers for ranges, procedure arrays, 3x3 matrices, white/black points, and 3D/4D lookup tables.
- `.setcieaspace`, `.setcieabcspace`, `.setciedefspace`, and `.setciedefgspace` build CIE color spaces, extract PostScript decode procedures, allocate lookup tables, prepare sampled caches, and set the graphics color space.
- `cie_set_finish` installs the color space, releases temporary references, records interpreter-side CIE procedures, and handles continuation completion.
- `cie_prepare_cache` pushes a sampling loop through the estack using `zfor_samples`; finish operators copy sampled results into `cie_cache_floats`.
- Finish callbacks replace decode functions with cache-backed implementations and call `gs_cie_*_complete`.

Dependencies and coupling:
- Bridges PostScript CIE dictionaries/procedures with graphics-library `gs_cie_*` structures.
- Uses estack continuations because arbitrary PostScript decode procedures must be sampled before the C color space can be completed.
- Careful about freeing color-space objects after `gs_setcolorspace` copies them.
