# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade1.c

`gxshade1.c` renders non-mesh shadings: function-based, axial, and radial. It builds patch/triangle representations and delegates actual subdivision/filling to patch helpers from `gxshade4.h` and related files.

For function-based shading, `gs_shading_Fb_fill_rectangle` transforms the target rectangle into the shading domain, evaluates the function at region corners, builds a four-sided patch with straight control poles, and calls `patch_fill`.

For axial shading, `gs_shading_A_fill_rectangle` maps the fill rectangle into a coordinate system where the shading axis is the parameter dimension. It computes the clipped parameter range, creates a parallelogram strip patch with endpoint parameter colors, and handles `Extend[0]`/`Extend[1]` by filling constant-color extension strips.

Radial shading is more complex. It represents interpolation between circles as annular tensor patches. Helpers construct quadrant arcs, outer extension circles, apex/cone fills, obtuse-cone triangles, and nested-circle extensions. `gs_shading_R_fill_rectangle` initializes patch state, paints optional start extension, the core annulus, and optional end extension.

The code uses visual-debug tracing hooks and has several comments marking approximations, especially for radial extension clipping. Risk areas include geometric degeneracy, radius/cone edge cases, and the apparent typo in `make_other_poles` where `control[1].x` is assigned but `control[1].y` is divided before being set.
