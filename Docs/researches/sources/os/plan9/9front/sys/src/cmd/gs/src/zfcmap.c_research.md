# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcmap.c

## Purpose
Creates internal Adobe CMap structures from PostScript CMap dictionaries and exposes `ztype0_get_cmap()` for Type 0 composite font construction.

## Key Functions
- `free_code_map()` releases lookup ranges and glyph value arrays after partial allocation failure.
- `acquire_code_ranges()` converts `.CodeMapData` code-space ranges into `gx_code_space_range_t` entries.
- `acquire_code_map()` converts definition/notdef code maps into `gx_cmap_lookup_range_t` arrays.
- `acquire_cid_system_info()` normalizes missing, dictionary, and array `CIDSystemInfo` values.
- `get_cid_system_info()` reads one CIDSystemInfo entry or creates a null entry.
- `ztype0_get_cmap()` extracts a built `CodeMap` struct from a Type 0 font dictionary and optionally checks subsidiary font CID compatibility.
- `zfcmap_glyph_name()` resolves glyph ids back to PostScript name strings.
- `zbuildcmap()` allocates and fills `gs_cmap_adobe1_t`, stores it under the CMap dictionary's `CodeMap`, and makes the dictionary readonly.

## Important Behavior
- `.CodeMapData` must be a three-element array: code ranges, def ranges, and notdef ranges.
- Code-map entries are five-tuples: prefix, misc bytes, key bytes, value data, and font index.
- Glyph-name values are accepted as arrays and converted to packed glyph ids.
- Missing `CIDSystemInfo` is tolerated by fabricating a zero-element array.
- CIDSystemInfo compatibility checking is compiled out by default because PLRM3 says interpreters need not check it.

## Research Notes
This is a parser/validator for the compact CMap representation prepared by Ghostscript PostScript support code. The actual lookup algorithms live in the graphics CMap layer.
