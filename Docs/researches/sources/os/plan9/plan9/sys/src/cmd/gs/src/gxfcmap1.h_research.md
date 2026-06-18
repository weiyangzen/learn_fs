# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcmap1.h

Defines concrete Adobe CMapType 1/2 implementation structures.

- Includes `gxfcmap.h`.
- Defines `gs_cmap_adobe1_t`, a concrete subclass of `gs_cmap_t`.
- Splits each map into:
  - key map from parsed character to value-table index
  - value table holding strings, names, or CIDs
- This split is designed to eventually allow related large CMaps to share value tables.
- Defines `gx_cmap_lookup_range_t`:
  - back pointer to CMap for glyph marking
  - entry count
  - shared key prefix
  - key size/range flag
  - packed key string
  - value type/size/string
  - font index
- Defines GC descriptors for lookup ranges, including glyph-name marking support.
- Defines:
  - `gx_code_space_t`
  - `gx_code_map_t`
- `gs_cmap_adobe1_s` contains common CMap fields plus:
  - code space
  - defined-character map
  - notdef map
  - glyph marking callback/data
- Declares `gs_cmap_adobe1_alloc`, which allocates and initializes the common structure plus storage for ranges/lookups/keys/values; caller fills actual data.

Role: concrete storage model for Adobe-style CMaps used by Ghostscript font/CID machinery.
