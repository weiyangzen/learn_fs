# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcmap.h

Defines internal CMap abstractions.

- CMaps map variable-length input characters to font-specific glyph/CID values.
- Supports Adobe-style CMaps while allowing virtual implementations such as direct TrueType `cmap` access.
- Defines `MAX_CMAP_CODE_SIZE` as 4.
- Defines `gx_code_space_range_t`:
  - first/last byte arrays
  - code size
- Defines lookup value types:
  - `CODE_VALUE_CID`
  - `CODE_VALUE_GLYPH`
  - `CODE_VALUE_CHARS`
  - `CODE_VALUE_NOTDEF`
- Defines `gx_cmap_lookup_entry_t`, covering range/single keys and string/name/CID-like values.
- Defines common CMap fields via `GS_CMAP_COMMON`:
  - `CMapType`
  - internal id
  - name
  - CID system info array
  - font count
  - version/UID/UIDOffset/WMode
  - Unicode/ToUnicode flags
  - glyph name callback
  - procedure vector
- Defines `gs_cmap_procs_t`:
  - `decode_next`
  - `enum_ranges`
  - `enum_lookups`
  - `is_identity`
- Defines range and lookup enumerator structures and procs.
- Provides client enumeration APIs:
  - `gs_cmap_ranges_enum_init`
  - `gs_cmap_enum_next_range`
  - `gs_cmap_lookups_enum_init`
  - `gs_cmap_enum_next_lookup`
  - `gs_cmap_enum_next_entry`
- Provides implementation helpers:
  - `gs_cmap_init`
  - `gs_cmap_alloc`
  - enumerator setup helpers
  - identity checks

Role: virtual base representation and traversal API for CMaps.
