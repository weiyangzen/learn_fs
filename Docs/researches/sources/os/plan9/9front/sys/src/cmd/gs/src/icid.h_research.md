# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icid.h

Declares CID font support helpers.

Key points:
- Forward-declares `gs_cid_system_info_t`.
- Declares parsing of `CIDSystemInfo` dictionaries.
- Declares CID-to-TrueType character code or glyph index conversion using `Decoding`, `TT_cmap`, and `SubstNWP`.
- Declares CIDMap construction from TrueType cmap data, decoding, substitution, and `GDBytes`.
- Declares `.type9mapcid` operator entry point.

Research notes:
- This header supports CID-keyed font mapping, especially TrueType-backed CID handling.
