# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcolor.h

Pattern color and rendered-tile structure declarations for Ghostscript.

Key contents:
- Defines `gs_pattern_type_t`, including callbacks for base-space use, pattern instantiation, template lookup, color remapping, and setcolor-time handling.
- Declares common pattern initialization/instantiation helpers and pattern instance freeing.
- Declares Pattern color space type and Pattern device color types for colored and masked uncolored patterns.
- Declares shared Pattern device-color serialization and nonzero-component methods.
- Defines `gx_color_tile`, the cache value/key for rendered PatternType 1 tiles: generated id, depth, template uid, tiling type, step matrix, bbox, color bits, mask, simplicity flag, dummy flag, and cache index.
- Defines `gx_device_pattern_accum`, a forwarding device wrapping memory devices for rendered pattern image and mask.
- Declares cache allocation, gstate cache access, accumulator allocation, cache insertion/dummy insertion, lookup, and selective purge functions.

Notable dependencies:
- `gspcolor.h`, `gxcspace.h`, `gxdevice.h`, `gxdevmem.h`, and `gxpcache.h`.

Research notes:
- The header notes that color depth alone is not enough to prove a cached tile matches a target device, because there is no full color-representation object.
- Non-zero bitmap shifts for tiles are explicitly unsupported.
