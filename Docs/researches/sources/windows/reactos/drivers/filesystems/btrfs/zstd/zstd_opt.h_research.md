# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_opt.h

## Scope And Purpose

`zstd_opt.h` declares the optimal-parser Zstd strategy entry points and the binary-tree update helper used during dictionary loading.

Complete file read: 56 lines.

## Public Interface

- `ZSTD_updateTree` updates the binary tree for dictionary content loading.
- No-dictionary optimal compressors:
  - `ZSTD_compressBlock_btopt`
  - `ZSTD_compressBlock_btultra`
  - `ZSTD_compressBlock_btultra2`
- Dictionary-match-state variants:
  - `ZSTD_compressBlock_btopt_dictMatchState`
  - `ZSTD_compressBlock_btultra_dictMatchState`
- External-dictionary variants:
  - `ZSTD_compressBlock_btopt_extDict`
  - `ZSTD_compressBlock_btultra_extDict`

## Integration Points

The header includes `zstd_compress_internal.h` for match-state and sequence-store types. It is consumed by the compressor strategy dispatcher and dictionary-loading paths.

## Notes

The header explicitly notes that `btultra2` has no dictionary or external-dictionary variant because it is intended only for the first block without prefix/dictionary history.
