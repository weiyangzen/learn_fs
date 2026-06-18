# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcid.c

Provides CMap and CID-keyed font utility routines.

Key behavior:
- `cid_system_info_param` extracts and validates `Registry`, `Ordering`, and `Supplement` from `CIDSystemInfo`.
- `TT_char_code_from_CID_no_subst` maps a CID through a `Decoding` dictionary and optional TrueType cmap array.
- `cid_to_TT_charcode` applies `SubstNWP` substitution ranges bidirectionally when direct CID mapping fails, returning source/destination substitution type refs.
- `set_CIDMap_element` stores 2-byte glyph indices into segmented string arrays representing a CIDMap.
- `cid_fill_CIDMap` validates `GDBytes == 2`, validates CIDMap array-of-strings structure, enumerates `Decoding`, resolves glyph indices with substitutions, and fills the CIDMap.

Dependencies and coupling:
- Used by CIDFont/CMap construction code rather than exposed directly as an operator table.
- Assumes `GDBytes == 2` and array-based CIDMap; other forms return `e_unregistered`.
