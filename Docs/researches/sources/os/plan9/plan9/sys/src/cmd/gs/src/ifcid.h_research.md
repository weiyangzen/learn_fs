# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifcid.h

Declares internal CID font helper APIs exported by `zfcid.c`.

Key points:
- `cid_font_system_info_param` extracts `CIDSystemInfo` from a CIDFont dictionary.
- `cid_font_data_param` extracts CIDFontType 0/2 data into `gs_font_cid_data`, including `GlyphDirectory`.

Research relevance:
- Narrow bridge for CID-keyed font dictionary parsing.
