# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcolor.h

This header defines Ghostscript's internal device color dispatch interface. It introduces `gx_rop_source_t` for RasterOp source data, the `gx_device_color_type_s` method vector, standard device color type symbols, color load/fill macros, and helpers for command-list color serialization.

`gx_rop_source_t` stores source bitmap data, source X offset, raster, bitmap id, optional source colors, and a `use_scolors` flag. The `gx_rop_no_source_body`, `gx_rop_source_set_color`, and `set_rop_no_source` helpers support RasterOp operations that conceptually lack a source operand.

`gx_device_color_type_s` is the key abstraction. Each device color variant provides methods for saving compact state, retrieving a device halftone, returning phase information, loading caches, filling rectangles, filling masks, equality checks, write/read serialization, and identifying non-zero color components for overprint handling.

The header documents command-list serialization semantics in detail: writers can omit repeated colors by comparing against a saved color, readers receive both imager state and prior device color, and halftones are serialized separately as all-band commands because they change infrequently.

The exported standard types are `gx_dc_type_none`, `gx_dc_type_null`, `gx_dc_type_pure`, `gx_dc_type_ht_binary`, `gx_dc_type_ht_colored`, and `gx_dc_type_wts`. It also exports non-zero-component helpers for pure and halftone colors, device-color type-index conversion, and canonical phase methods.

Convenience macros route common operations through the active color type: `gx_color_load`, `gx_device_color_fill_rectangle`, and `gx_fill_rectangle*`. `gx_set_dev_color` triggers `gx_remap_color` when the graphics state's current device color is unset.

Filesystem relevance: none directly. It is a graphics rendering contract within the Ghostscript subtree.
