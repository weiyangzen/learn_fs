# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_ldm.h

## Scope And Purpose

`zstd_ldm.h` declares the long-distance matching API used by Zstd compression.

Complete file read: 110 lines.

## Public Interface

- `ZSTD_LDM_DEFAULT_WINDOW_LOG` aliases the default window-log limit.
- `ZSTD_ldm_fillHashTable` preloads LDM entries for a byte range.
- `ZSTD_ldm_generateSequences` produces long-distance `rawSeq` matches for a source range.
- `ZSTD_ldm_blockCompress` compresses a block while consuming predefined raw LDM sequences and a normal secondary block compressor.
- `ZSTD_ldm_skipSequences` advances raw sequences for data not passed to block compression.
- `ZSTD_ldm_getTableSize` estimates LDM table workspace.
- `ZSTD_ldm_getMaxNbSeq` estimates the maximum number of raw sequences.
- `ZSTD_ldm_adjustParameters` normalizes LDM parameters against regular compression parameters.

## Integration Points

The header includes `zstd_compress_internal.h` for LDM state and sequence types and `zstd.h` for public compression parameter types. It is consumed primarily by `zstd_compress.c`.

## Notes

The comments document important caller contracts: the Zstd window must be updated before sequence generation, the raw sequence store must be large enough, and predefined sequences can span block boundaries.
