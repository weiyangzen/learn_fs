# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifcid.h

Declares internal CID font helper APIs exported by `zfcid.c`.

Key points:
- `cid_font_system_info_param` extracts `CIDSystemInfo` from a CIDFont dictionary.
- `cid_font_data_param` extracts additional CIDFontType 0/2 data into `gs_font_cid_data`, including `GlyphDirectory`.

Dependencies and interactions:
- Uses `gs_cid_system_info_t`, `ref`, `os_ptr`, and `gs_font_cid_data`.
- Used by CID font builders/operators.

Research relevance:
- Small bridge header for CID-keyed font dictionary parsing.
