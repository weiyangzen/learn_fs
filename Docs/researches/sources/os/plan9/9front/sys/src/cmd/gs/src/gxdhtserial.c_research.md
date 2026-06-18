# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdhtserial.c

This file serializes and deserializes traditional Ghostscript device halftones for command-list transmission. It covers transfer maps, halftone order components, complete multi-component device halftones, and read-and-install behavior on the renderer side.

`gx_ht_write_tf` serializes an optional transfer function as one byte for absent or identity maps, or as a type byte plus the full transfer value array for complete mapped transfers. `gx_ht_read_tf` reconstructs a transfer map, allocating `gx_transfer_map`, assigning a new id, initializing identity or mapped procedures, and returning bytes consumed.

`gx_ht_write_component` serializes one `gx_ht_order_component`, but only the order data needed by a renderer. It rejects WTS orders as unsupported for this serializer. It omits construction-only or renderer-local fields such as cell params, WTS enum data, raster, original height/shift, full height, allocation memory, cache, and screen params. It writes order type, width, height, shift, level count, bit count, procs-table index, levels array, bit-data array, and transfer function.

`gx_ht_read_component` reverses that format. It validates the traditional order type, decodes dimensions/counts/procs, allocates levels and bit data with `gx_ht_alloc_ht_order`, clears historical params/screen fields, copies serialized arrays, reads the transfer function, then searches resident halftone resources for matching levels and bit data. On a match it frees the newly allocated arrays and points at the resident resource arrays.

`gx_ht_write` serializes a full device halftone. It asserts a component-array-based halftone, writes the halftone type and number of device components, then serializes each component. It intentionally does not transmit reference count, id, primary `order`, or LCM dimensions because those are recreated or ignored by the reader.

`gx_ht_read_and_install` reads the serialized type and components into a stack `gx_device_halftone`, installs it through `gx_imager_dev_ht_install`, and releases allocated component orders on failure. Combining read and install avoids heap-allocating a full halftone object just to install and discard it.

Filesystem relevance: indirect only. This is command-list serialization for rendering state, not filesystem serialization or storage format code.
