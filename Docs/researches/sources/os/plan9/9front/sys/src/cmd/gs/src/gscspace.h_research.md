# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscspace.h

This is the central public color-space header. It documents and defines Ghostscript’s inline color-space hierarchy, including small base spaces, regular base spaces, direct spaces, paint spaces, and fully general spaces.

Important definitions:
- `gs_color_space_index` enumerates Device, CIE, Separation, Indexed, Pattern, DeviceN, DevicePixel, and ICCBased spaces.
- `gs_cspace_common` defines the shared object header: type vector, memory pointer, ID, and parameter union.
- `gs_small_base_color_space`, `gs_base_color_space`, `gs_direct_color_space`, `gs_paint_color_space`, and `gs_color_space` encode progressively larger inline structures.
- Separation and DeviceN parameters include component names, alternate base color space, `gs_device_n_map`, `use_alt_cspace`, and color-name string callbacks.
- Indexed spaces embed a direct base space and either a lookup table or lookup procedure.
- Pattern spaces may embed a paint color space.

The long design comment is important: ICCBased spaces complicated the original hierarchy, but the implementation keeps inline embedding for compatibility and performance, relying on caller discipline for copy size safety.

Public procedures cover construction of Device spaces, copying/assignment/release, component counts, equality, color restriction, and base/alternate color-space lookup.

This header underpins nearly every color-related file in the batch, including Separation, substitution, equivalent spot color capture, and device color remapping.
