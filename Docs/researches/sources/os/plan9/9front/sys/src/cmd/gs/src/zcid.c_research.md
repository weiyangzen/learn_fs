# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcid.c

This file provides CMap and CID-keyed font service routines.

Key behavior:
- `cid_system_info_param` extracts and validates `Registry`, `Ordering`, and `Supplement` from a CIDSystemInfo dictionary.
- Converts CIDs to TrueType character codes or glyph indexes using a Decoding dictionary and optional TrueType cmap.
- Applies `SubstNWP` substitution ranges in both directions when direct CID lookup fails.
- Builds a GDBytes=2 CIDMap from Decoding, TrueType cmap, and SubstNWP by writing glyph indexes into CIDMap strings.
- Validates CIDMap array/string shape before filling it.

Important dependencies:
- Uses CID structures from `gxcid.h` and `icid.h`.
- Uses Ghostscript dictionary and array APIs from `idict.h`, `idparam.h`, and `store.h`.

Research notes:
- This file does not register PostScript operators directly; it is support code for CID font/CMap construction.
- Several comments mark unimplemented general cases, including non-2-byte GDBytes and non-array CIDMap forms.
