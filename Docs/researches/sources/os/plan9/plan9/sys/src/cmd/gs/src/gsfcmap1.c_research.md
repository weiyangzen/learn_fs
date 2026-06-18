# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcmap1.c

## Role

`gsfcmap1.c` implements Adobe-style CMap decoding with code-space ranges, defined/notdef lookup tables, multidimensional range offsets, lookup enumeration, and allocation.

## Decode Logic

`code_map_decode_next_multidim_regime` scans lookup ranges in reverse order to honor `usecmap` override behavior. It handles key prefixes, partial matches, range keys, and value types:

- CID
- NOTDEF
- GLYPH
- CHARS

For CID ranges, it computes multidimensional offsets so the last byte changes fastest. For `CHARS`, it returns value size and computes character code offset from the range start.

`gs_cmap_adobe1_decode_next` first checks defined mappings. If none match, it checks notdef mappings. If neither matches, it uses partial-match fallback or consumes the shortest defined character length and maps to CID 0. Too-short undecodable input returns `rangecheck`.

The comments note codespace ranges are not currently enforced during decode.

## Enumeration/Allocation

Range enumeration walks `code_space.ranges`. Lookup enumeration supports defined and notdef maps separately. `gs_cmap_adobe1_alloc` allocates ranges, lookup structs, key/value buffers, base CMap state, initializes lookup ownership, and leaves caller to populate tables.

## Dependencies

Uses `gxfcmap1.h`, CMap allocation helpers from `gsfcmap.c`, memory, IDs, debugging helpers, and error codes.

## Risks

Lookup search is linear and can be expensive for large CMaps. Decode accepts mappings outside codespace ranges. Allocation error cleanup does not visibly free a successfully allocated base `pcmap` when later allocations fail, so ownership/error cleanup should be reviewed in context.
