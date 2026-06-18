# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcmap.c

## Role

`gsfcmap.c` implements generic CMap client operations, identity CMaps, CMap allocation/enumeration helpers, identity detection, and ToUnicode CMaps.

## Identity CMaps

`gs_cmap_identity_t` stores byte width, varying byte count, and return-code mode. Identity decode reads a big-endian code, returns CID glyph `gs_min_cid_glyph + value`, updates index/font index, and may return the code byte count for character identity maps.

Identity range/lookup enumeration exposes full byte ranges. Public constructors are:

- `gs_cmap_create_identity`
- `gs_cmap_create_char_identity`

Both currently require `num_bytes == 2`.

## Generic CMap API

Implements:

- `gs_cmap_is_identity`
- `gs_cmap_decode_next`
- range and lookup enumeration init/next helpers
- `gs_cmap_init`
- `gs_cmap_alloc`
- enum setup helpers
- `gs_cmap_compute_identity`

`gs_cmap_alloc` reserves IDs for subfont-related use, allocates CIDSystemInfo array, sets CMap metadata, WMode, and procedure vector.

## ToUnicode

Defines a compact `gs_cmap_ToUnicode_t` with a dense two-byte Unicode map. It supports allocation, pair insertion, range/lookup enumeration, and identity tracking. Decode is deliberately unsupported with `assert(0)` because this path is not used for decoding.

## Dependencies

Uses CMap internals (`gxfcmap.h`), CIDSystemInfo descriptors, memory, IDs, and errors.

## Risks

ToUnicode allocation leaks the CMap if subsequent map allocation fails. ToUnicode lookup enumeration hardcodes two-byte Unicode values. Identity constructors reject non-two-byte maps despite comments describing possible generalization.
