# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfont0c.h

Declares helper APIs for creating Type 0 wrappers and CID/CMap conversions.

Key declarations:
- `gs_font_type0_from_cidfont` creates a Type 0 wrapper for a CIDFont, with optional matrix and WMode.
- `gs_font_type0_from_type42` creates a Type 0 wrapper around a Type 42 font converted to a Type 2 CIDFont, optionally using the TrueType cmap.
- `gs_font_cid2_from_type42` converts a Type 42 font into a Type 2 CIDFont.
- `gs_cmap_from_type42_cmap` creates a Unicode-based CMap from a TrueType Platform 3, Encoding 1, Format 4 cmap.

Dependencies:
- Includes `gxfont0.h` and `gxfcid.h`.

Research notes:
- This is glue between simple TrueType/CID font representations and composite Type 0 font machinery.
- The CMap helper is intentionally limited to a specific TrueType cmap format.
