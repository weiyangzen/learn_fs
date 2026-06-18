# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcmap.c

This file implements public CMap allocation, identity CMaps, decoding dispatch, enumeration dispatch, identity checking, and ToUnicode CMaps.

Identity CMaps:
- `gs_cmap_create_identity` creates Identity-H/V style CID mappings.
- `gs_cmap_create_char_identity` creates Identity-BF-H/V mappings that return character codes instead of CIDs.
- Identity decode reads a fixed-width big-endian integer and maps it to `gs_min_cid_glyph + value`.

Common CMap support:
- `gs_cmap_init` clears common fields, assigns reserved IDs, and invalidates UID.
- `gs_cmap_alloc` allocates a CMap plus CIDSystemInfo array and fills common metadata.
- Decode/range/lookup functions dispatch through `pcmap->procs`.
- `gs_cmap_compute_identity` enumerates mappings and checks whether keys equal CID values.

ToUnicode CMaps:
- `gs_cmap_ToUnicode_alloc` allocates a compact two-byte Unicode map array.
- `gs_cmap_ToUnicode_add_pair` records source-code to Unicode pairs and updates an `is_identity` flag.
- ToUnicode decoding itself asserts unsupported because this form is intended for enumeration/output, not runtime decoding.
- Lookup enumeration groups consecutive Unicode values into ranges suitable for PDF-style output.

This file is the base implementation used by Adobe CMaps in `gsfcmap1.c` and Type42-derived CMaps in `gsfcid2.c`.
