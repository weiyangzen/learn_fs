# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcmap1.c

This file implements Adobe-style CMap decoding with multi-dimensional ranges, partial-match fallback, `.notdef` maps, lookup enumeration, and allocation.

Key logic:
- `code_map_decode_next_multidim_regime` scans lookup ranges in reverse order so later/usecmap entries override earlier ones.
- It handles key prefixes, exact matches, partial matches, range keys, CID offsets, glyph values, character-code values, and `.notdef` values.
- `gs_multidim_CID_offset` computes offsets for multi-byte range dimensions where the last byte changes fastest.
- `gs_cmap_adobe1_decode_next` first checks defined mappings, then `.notdef` mappings, then applies PostScript CMap fallback rules.
- If no partial match exists, it consumes the shortest defined character length and maps to CID 0 when enough bytes remain; otherwise it returns `rangecheck`.

Enumeration:
- Range enumeration returns code-space ranges.
- Lookup enumeration separately exposes defined and notdef maps.
- Entry enumeration combines prefixes and keys into full key boundaries.

Allocation:
- `gs_cmap_adobe1_alloc` allocates the CMap, code-space range array, lookup range array, key storage, and value storage, then wires the first lookup to the shared key/value buffers.

GC handling:
- Lookup ranges trace their parent CMap, key/value strings, and mark glyph values when value type is `CODE_VALUE_GLYPH`.

The file implements the complex runtime behavior behind parsed Adobe CMaps.
