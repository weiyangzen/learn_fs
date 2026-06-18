# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscssub.c

This file implements library-level color-space substitution for DeviceGray, DeviceRGB, and DeviceCMYK when `UseCIEColor` is active.

Main functions:
- `gs_setsubstitutecolorspace` installs or clears a substitute color space in `pgs->device_color_spaces`.
- `gs_current_DeviceGray_space`, `gs_current_DeviceRGB_space`, and `gs_current_DeviceCMYK_space` return either the active substitute or the shared default.
- `gs_currentsubstitutecolorspace` dispatches by `gs_color_space_index`.

The code allows ICCBased substitutes when component counts match the target Device space. For non-ICCBased spaces, it appears intended to validate against per-device masks for Device/CIE-compatible spaces.

Lifecycle behavior:
- If no substitute object exists yet, it allocates a `gs_color_space`, initializes it from the provided space, and stores it in the graphics state.
- If one already exists, it uses `gs_cspace_assign`, preserving reference-count semantics.
- Passing `NULL` resets to the shared default device color space.

Potential maintenance note: the mask check uses `else if (!masks[index] && (1 << gs_color_space_get_index(pcs)))`, which is always false for the defined nonzero masks. This looks like it may have intended `!(masks[index] & ...)`.
