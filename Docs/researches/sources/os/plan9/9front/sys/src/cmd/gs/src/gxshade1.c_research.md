# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade1.c

Rendering for non-mesh shadings: function-based type 1, axial type 2, and radial type 3. It converts these shading forms into patch/triangle fill operations shared with mesh shading code.

Key behavior:
- Function-based shading computes the inverse parameter range for the target rectangle, evaluates the function at the four parameter-space corners, builds a synthetic patch, and calls `patch_fill`.
- Axial shading builds a coordinate frame where the axial line is the parameter direction, clips the requested fill rectangle to `[0,1]`, fills the main band, and optionally fills extension bands at constant endpoint colors.
- Radial shading represents the interpolation between two circles using annular tensor patches and handles extension regions for nested, obtuse-cone, acute-cone, cylinder, and apex cases.
- `R_tensor_annulus` decomposes circle annulus portions into four patch quadrants using Bezier quadrant arcs.
- `R_outer_circle`, `R_rect_radius`, `R_obtuse_cone`, `R_tensor_cone_apex`, and `R_extensions` compute geometry needed for radial extension regions.
- Visual debug tracing hooks exist for axial, radial, and function-based patch rendering.

Notable dependencies:
- Function/pattern and color support: `gsptype2.h`, `gxcspace.h`, `gxdcolor.h`.
- Path and shading internals: `gxpath.h`, `gxshade.h`, `gxshade4.h`.
- Device client and imager state: `gxdevcli.h`, `gxistate.h`.

Research notes:
- `make_other_poles` appears to contain a real assignment-order typo: `curve[i].control[1].y /= 3;` is executed before `control[1].y` is assigned from vertex coordinates.
- `gs_shading_R_fill_rectangle` releases visual tracing with `VD_TRACE_FUNCTIONAL_PATCH` rather than `VD_TRACE_RADIAL_PATCH`, which looks like a copy/paste inconsistency.
- The radial extension logic is geometry-heavy and contains comments acknowledging approximations, such as not cutting invisible annulus parts.
