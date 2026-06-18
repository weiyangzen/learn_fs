# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscsepr.h

This header exposes the client API for Ghostscript Separation color spaces. It depends on `gscspace.h` for `gs_color_space`, `gs_separation_name`, and the general color-space hierarchy.

Key interfaces:
- `gs_cspace_build_Separation` allocates and builds a Separation color space.
- `gs_build_Separation` initializes the central Separation state inside an already allocated `gs_color_space`.
- `gs_cspace_set_sepr_proc` installs a tint transform callback.
- `gs_cspace_set_sepr_function` and `gs_cspace_get_sepr_function` bind or retrieve a `gs_function_t` tint transform.

The comments document an important design change: Separation is treated as a single-component DeviceN color space, except `/All` and `/None`, which retain special handling. The old multi-entry tint cache is gone; tint transforms execute as needed and must not require interpreter callbacks.

Integration points are `gscsepr.c`, interpreter setup in `zcssepr.c`, and PDF/vector code that may query the tint transform function, such as `gdevpdfc.c`.
