# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxhttile.h

## Role

`gxhttile.h` defines the `gx_ht_tile` structure used by halftone caches and device colors.

This is imaging/halftone infrastructure, not filesystem code.

## Main Definition

- `gx_ht_tile` contains:
  - `gx_strip_bitmap tiles`: the currently rendered/repeated bitmap tile.
  - `int level`: cached gray level, described as number of spots whitened, or `-1` for empty.
  - `uint index`: tile index within the cache, used by GC relocation.

## Dependencies

- Requires `gxbitmap.h` to define `gx_strip_bitmap`.
- Forward declares `gx_ht_tile` under `gx_ht_tile_DEFINED`.

## Notable Risks

- Cache correctness depends on `level` matching the actual contents of `tiles.data`.
- `index` is part of pointer relocation for cached tile arrays; changing layout affects GC support in `gxht.c`.
