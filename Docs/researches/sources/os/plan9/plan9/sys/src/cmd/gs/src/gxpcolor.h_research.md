# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcolor.h

`gxpcolor.h` declares internal Pattern color, tile, cache, and accumulator APIs. It includes pattern, color-space, device, memory-device, and cache headers.

`gs_pattern_type_s` is a dispatch table for pattern behavior: whether base color space is used, making an instance, retrieving a template, remapping color, and setcolor-time actions. The header declares common template/instance helpers and the Pattern color-space type.

The file declares Pattern device-color types for colored and uncolored masked variants, plus shared device-color serialization and nonzero-component methods.

`gx_color_tile_s` is the cache entry format. Its key fields are generated bitmap id, depth, and copied template UID; value fields include tiling type, step matrix, bbox, color bits, mask bits, simple/dummy flags, and index. Nonzero bitmap shifts are explicitly unsupported.

The header also declares default cache sizing, cache allocation, gstate cache accessors, accumulator allocation, cache insertion/dummy insertion, lookup, and selective winnowing. `gx_device_pattern_accum` wraps forward-device common fields with bitmap memory, pattern instance, color bits, and mask devices.

This is the main contract between pattern interpretation, rendering, and device-color use.
