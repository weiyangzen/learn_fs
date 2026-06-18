# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcmap1.h

This header defines the concrete Adobe CMapType 1/2 implementation subclass for the generic CMap interface in `gxfcmap.h`.

The design separates each map into a key map and a value table, allowing related large CMaps to potentially share value tables while using different code spaces or key maps.

`gx_cmap_lookup_range_t` stores one lookup range: back pointer to the owning Adobe CMap, entry count, shared key prefix, key size, range flag, packed keys, value type, value size, packed values, and font index. GC descriptors are complex because lookup ranges may reference names that need marking.

`gx_code_space_t` owns an array of code-space ranges. `gx_code_map_t` owns an array of lookup ranges. `gs_cmap_adobe1_t` embeds `GS_CMAP_COMMON`, then adds code space, defined-character map, notdef map, glyph marking callback, and callback data.

`gs_cmap_adobe1_alloc` allocates and initializes an Adobe1 CMap with requested counts and packed key/value storage sizes; the caller still fills code ranges, lookup tables, keys, and values.

Filesystem relevance: none. It is concrete font CMap mapping data.
