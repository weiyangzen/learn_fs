# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_double_fast.h

## Summary
Declares the double-fast compression strategy helpers.

## Key APIs
- `ZSTD_fillDoubleHashTable()`.
- `ZSTD_compressBlock_doubleFast()`.
- `ZSTD_compressBlock_doubleFast_dictMatchState()`.
- `ZSTD_compressBlock_doubleFast_extDict()`.

## Important Behavior
The prototypes operate on `ZSTD_matchState_t`, `seqStore_t`, repeat-code arrays, and a source block. Separate entry points cover no-dictionary, attached dictionary match state, and external dictionary modes.

## Risks
This is an internal strategy header. Callers must provide initialized match-state hash/chain tables, compression parameters, window metadata, and valid repeat-code state.
