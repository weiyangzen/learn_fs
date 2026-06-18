# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevcli.h

This is the primary Ghostscript device-client interface. It defines the `gx_device` object contract, device reference-counting rules, page-device hooks, color model metadata, the complete device procedure vector, image data helpers, forwarding/null device types, and device lifecycle helpers.

The opening documentation is important for memory ownership: device instances are reference-counted, may be marked retained, and must use `gx_device_set_target` rather than direct assignment for forwarding-device targets. It distinguishes dynamically copied devices, local/static instances, and embedded instances, warning that stack/static devices must be retained or initialized with NULL memory.

The auxiliary type section forward-declares graphics state, paths, clipping paths, image enumerators, patterns, and fill/stroke parameters. It defines `gx_drawing_color` as `gx_device_color`, anti-aliasing info, fixed-edge structures, linear-color edge structures, `frac31`, and enums for color separability/linearity, polarity, and overprint mode.

`gx_device_color_info` is the expanded process color model descriptor. It records maximum and active component counts, polarity, encoded depth, gray component index, max/dither levels, anti-aliasing bits, separable/linear encoding data (`comp_shift`, `comp_bits`, `comp_mask`), process color model name, overprint mode, and process component mask. The surrounding macros provide compatibility initializers such as `dci_alpha_values`, `dci_std_color`, `dci_black_and_white`, and process color model name access.

`gx_page_device_procs` supplies page-level install/begin/end hooks. `gx_device_common` defines the common fields of all devices: parameter size, proc records, name, memory/type/finalization fields, reference-count state, open state, fill-band limit, color info/cache, geometry, media, margins, page counters, safety flags, page procedures, and the embedded `gx_device_procs` procedure record.

The device procedure macros declare the full driver API: open/close/sync/output, matrix setup, color mapping, rectangle/tile/copy drawing, bitmap access, parameters, xfont, alpha, banding, RasterOp, path/stroke/mask/trapezoid/parallelogram/triangle/thin-line drawing, image begin/data/end, strip tiling, clipping box, typed images, bits rectangles, compositors, hardware params, text, transparency groups/masks, DeviceN color mapping, pattern management, high-level colors, included color spaces, linear-color fills, and spot equivalent color updates.

`gx_device_proc_struct(dev_t)` expands to the actual procedure-vector layout. The order of members is therefore ABI-like inside this codebase and must match device initializers and default proc filling.

Image handling helpers define `gx_image_plane_t`, wrappers for begin image/typed image, and the modern enumerator-associated data/end functions (`gx_image_data`, `gx_image_plane_data`, `gx_image_plane_data_rows`, `gx_image_flush`, `gx_image_planes_wanted`, `gx_image_end`). Older driver-like wrappers are retained for compatibility.

The bottom of the file defines generic `gx_device`, `gx_device_forward`, and `gx_device_null` structures, GC descriptors, null-device helpers, target setting, retained status management, raster calculation, geometry/resolution/media setters, device switching, closing, local finalization, and an unused `gx_device_type` concept.

Filesystem relevance: none directly. It is a driver/device abstraction for Ghostscript rendering devices, not Plan 9 kernel devices or filesystems.
