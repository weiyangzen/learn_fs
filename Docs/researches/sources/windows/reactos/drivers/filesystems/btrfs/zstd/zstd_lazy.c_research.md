# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_lazy.c

## Scope And Purpose

`zstd_lazy.c` implements Zstd greedy, lazy, lazy2, and btlazy2 block compression strategies. It provides both hash-chain and binary-tree match finders and supports normal prefix compression, dictionary-match-state compression, and external-dictionary compression.

Complete file read: 1138 lines.

## Main Components

- Binary-tree logic:
  - `ZSTD_updateDUBT` inserts unsorted positions into a deferred-update binary tree.
  - `ZSTD_insertDUBT1` sorts one pending candidate.
  - `ZSTD_DUBT_findBestMatch` and `ZSTD_DUBT_findBetterDictMatch` search sorted candidates and optional dictionary match state for the best match.
  - `ZSTD_BtFindBestMatch*` wrappers dispatch by `minMatch` and dictionary mode.
- Hash-chain logic:
  - `ZSTD_insertAndFindFirstIndex_internal` updates the hash chain to the current input.
  - `ZSTD_insertAndFindFirstIndex` exposes that helper for other modules.
  - `ZSTD_HcFindBestMatch_generic` searches hash-chain candidates and optional dictionary chains.
- Lazy parser:
  - `ZSTD_compressBlock_lazy_generic` is the shared normal/dictionary-match-state parser. It checks repcodes, asks the selected match finder for candidates, optionally probes one or two bytes ahead, stores chosen sequences, and updates repcodes.
  - `ZSTD_compressBlock_lazy_extDict_generic` mirrors the parser for external dictionary windows with two-segment matching.
- Public wrappers select parser depth and match finder:
  - Greedy: depth 0, hash chain.
  - Lazy: depth 1, hash chain.
  - Lazy2: depth 2, hash chain.
  - Btlazy2: depth 2, binary tree.
  - Each has no-dictionary, dictionary-match-state, and external-dictionary variants where applicable.

## Integration Points

The file is called through the compressor strategy table in `zstd_compress.c`. It depends on `ZSTD_storeSeq`, window bounds, repcode rules, `ZSTD_count`, `ZSTD_count_2segments`, hash helpers, and compression parameters from `zstd_compress_internal.h`.

## Notes

- The deferred binary tree trades delayed sorting work for faster insertion.
- Pointer and index arithmetic intentionally uses unsigned overflow patterns in several boundary checks.
- Compression ratio and CPU cost are controlled mainly by `searchLog`, `chainLog`, `targetLength`, parser depth, and whether the binary tree is used.
