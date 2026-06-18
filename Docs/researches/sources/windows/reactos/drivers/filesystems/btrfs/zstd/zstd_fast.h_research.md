# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_fast.h

## Scope And Purpose

`zstd_fast.h` declares the fast Zstd block-compression strategy entry points used by the shared compressor dispatcher.

Complete file read: 37 lines.

## Public Interface

- `ZSTD_fillHashTable` fills a `ZSTD_matchState_t` hash table up to a supplied end pointer using a selected dictionary-table load method.
- `ZSTD_compressBlock_fast` compresses one block with the fast parser and no attached dictionary match state.
- `ZSTD_compressBlock_fast_dictMatchState` compresses with a separate dictionary match state.
- `ZSTD_compressBlock_fast_extDict` compresses with an external dictionary window.

## Integration Points

The header includes `mem.h` for fixed-width Zstd types and `zstd_compress_internal.h` for match-state, sequence-store, repcode, and dictionary-mode definitions. It uses `extern "C"` guards for C++ compatibility.

## Notes

This header is purely declarative and has no local logic. Its declarations are consumed by `zstd_compress.c`, `zstd_ldm.c`, and other strategy-selection code.
