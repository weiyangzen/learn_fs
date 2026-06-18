# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfcmap.c

## Purpose
Creates internal Adobe CMap structures from PostScript CMap dictionaries and exposes `ztype0_get_cmap()` for Type 0 composite font construction.

## Key Functions
- `acquire_code_ranges()` converts `.CodeMapData` code-space ranges into `gx_code_space_range_t` entries.
- `acquire_code_map()` converts definition/notdef code maps into `gx_cmap_lookup_range_t` arrays.
- `ztype0_get_cmap()` extracts a built `CodeMap` struct from a Type 0 font dictionary.
- `zbuildcmap()` allocates and fills `gs_cmap_adobe1_t`, stores it under `CodeMap`, and makes the dictionary readonly.

## Important Behavior
- `.CodeMapData` must be a three-element array: code ranges, def ranges, and notdef ranges.
- Code-map entries are five-tuples: prefix, misc bytes, key bytes, value data, and font index.
- Missing `CIDSystemInfo` is tolerated by fabricating a zero-element array.
- CIDSystemInfo compatibility checking is compiled out by default.

## Research Notes
This is a parser/validator for the compact CMap representation prepared by Ghostscript PostScript support code.
