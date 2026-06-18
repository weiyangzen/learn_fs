# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_lazy.h

## Scope And Purpose

`zstd_lazy.h` declares the lazy-family Zstd block-compressor entry points and one hash-chain helper.

Complete file read: 67 lines.

## Public Interface

- `ZSTD_insertAndFindFirstIndex` updates the match-state hash chain and returns the first candidate index.
- `ZSTD_preserveUnsortedMark` is declared for index-reduction handling of deferred binary-tree unsorted markers.
- Normal block compressors:
  - `ZSTD_compressBlock_btlazy2`
  - `ZSTD_compressBlock_lazy2`
  - `ZSTD_compressBlock_lazy`
  - `ZSTD_compressBlock_greedy`
- Dictionary-match-state variants:
  - `ZSTD_compressBlock_btlazy2_dictMatchState`
  - `ZSTD_compressBlock_lazy2_dictMatchState`
  - `ZSTD_compressBlock_lazy_dictMatchState`
  - `ZSTD_compressBlock_greedy_dictMatchState`
- External-dictionary variants:
  - `ZSTD_compressBlock_greedy_extDict`
  - `ZSTD_compressBlock_lazy_extDict`
  - `ZSTD_compressBlock_lazy2_extDict`
  - `ZSTD_compressBlock_btlazy2_extDict`

## Integration Points

The header includes `zstd_compress_internal.h` and is consumed by `zstd_compress.c` strategy dispatch plus modules that need hash-chain insertion.

## Notes

This header exposes strategy variants only; parser implementation and match-finder behavior live in `zstd_lazy.c`.
