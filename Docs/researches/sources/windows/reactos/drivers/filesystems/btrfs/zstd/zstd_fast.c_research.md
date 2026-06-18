# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_fast.c

## Scope And Purpose

`zstd_fast.c` implements Zstd's fast block parser for the ReactOS Btrfs bundled Zstd library. It maintains hash tables, finds short prefix/dictionary matches, emits sequences into `seqStore_t`, and updates repeated offsets for later blocks.

Complete file read: 496 lines.

## Main Components

- `ZSTD_fillHashTable` preloads the match-state hash table from `ms->nextToUpdate` to an end pointer, either sparsely for fast dictionary-table load or more fully when requested.
- `ZSTD_compressBlock_fast_generic` is the core no-dictionary fast parser. It checks two adjacent candidates per loop, handles immediate repcode matches, stores regular match sequences, and skips faster through incompressible input.
- `ZSTD_compressBlock_fast` dispatches the generic parser by `minMatch` length.
- `ZSTD_compressBlock_fast_dictMatchState_generic` adds lookup against an attached dictionary match state and bridges matches spanning dictionary and prefix memory.
- `ZSTD_compressBlock_fast_dictMatchState` dispatches the dictionary-match-state variant by `minMatch`.
- `ZSTD_compressBlock_fast_extDict_generic` handles external dictionary windows through two-segment match counting and falls back to the normal fast parser if the external dictionary has been invalidated.
- `ZSTD_compressBlock_fast_extDict` dispatches the external-dictionary variant by `minMatch`.

## Integration Points

This file is selected by `ZSTD_selectBlockCompressor()` in `zstd_compress.c` for `ZSTD_fast` strategy and its dictionary modes. It depends on `ZSTD_matchState_t`, `ZSTD_hashPtr`, `ZSTD_count`, `ZSTD_count_2segments`, `ZSTD_storeSeq`, repeated-offset constants, and window helpers from `zstd_compress_internal.h`.

## Notes

- Match search is intentionally shallow and biased toward speed.
- Repcode invalidation is handled by zeroing offsets outside the valid prefix window.
- Dictionary handling is pointer-arithmetic heavy; correctness depends on `dictLimit`, `lowLimit`, `dictIndexDelta`, and prefix/dictionary boundaries being maintained by the caller.
