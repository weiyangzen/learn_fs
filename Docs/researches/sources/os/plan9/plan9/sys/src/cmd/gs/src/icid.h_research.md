# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/icid.h

CID font interface header for `zcid.c` and `zfcid0.c`.

Exports:
- `cid_system_info_param`
- `cid_to_TT_charcode`
- `cid_fill_CIDMap`
- `ztype9mapcid`

It supports CIDSystemInfo parsing and CID-to-TrueType charcode/glyph mapping using Decoding, TT cmap, and SubstNWP data.
