# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscspace.c

This file implements core color-space support for the Ghostscript graphics library. It defines the standard DeviceGray, DeviceRGB, and DeviceCMYK color-space type vectors, including component counts, remap/concretize hooks, overprint behavior, serialization, and linearity tests.

Major responsibilities:
- Allocates, initializes, copies, assigns, and releases `gs_color_space` objects.
- Provides static prototypes for parameterless Device color spaces.
- Implements public accessors such as `gs_color_space_get_index`, `gs_color_space_num_components`, `gs_color_space_restrict_color`, and `gs_cspace_base_space`.
- Handles reference-count adjustment through color-space type methods.
- Implements DeviceCMYK-specific overprint handling, including process-component detection on devices with Cyan/Magenta/Yellow/Black components.
- Provides default linearity checks used by shaded fills or optimized interpolation paths.

The file is sensitive to memory layout. `cs_copy` copies only `pcsfrom->type->stype->ssize`, matching the variable-sized inline color-space hierarchy defined in `gscspace.h`.

Device interaction is significant: overprint logic consults device component names and color-mapping procedures, updates `gs_overprint_params_t`, and may inspect current `gx_device_color` nonzero components.

Potential maintenance note: this code assumes callers only copy into destinations large enough for the actual color-space subtype, matching the warning in `gscspace.h`.
