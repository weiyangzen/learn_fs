# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_ldm.c

## Scope And Purpose

`zstd_ldm.c` implements Zstd long-distance matching. It finds large repeated regions beyond normal block match-finder reach, stores them as raw sequences, and then interleaves those predefined sequences with the selected normal block compressor.

Complete file read: 619 lines.

## Main Components

- Parameter sizing:
  - `ZSTD_ldm_adjustParameters` fills defaults for window, bucket size, minimum match length, hash log, and sampling rate.
  - `ZSTD_ldm_getTableSize` estimates hash/bucket workspace size.
  - `ZSTD_ldm_getMaxNbSeq` estimates raw sequence capacity.
- Hashing and buckets:
  - `ZSTD_ldm_getSmallHash`, `ZSTD_ldm_getChecksum`, and `ZSTD_ldm_getTag` split a rolling hash into bucket index, checksum, and sampling tag.
  - `ZSTD_ldm_getBucket`, `ZSTD_ldm_insertEntry`, and `ZSTD_ldm_makeEntryAndInsertByTag` manage circular bucket entries.
  - `ZSTD_ldm_fillHashTable` preloads the LDM table over a range.
- Sequence generation:
  - `ZSTD_ldm_generateSequences_internal` rolls through input, samples tagged positions, scans candidate buckets, extends matches forward and backward, emits `rawSeq` records, and fills the table after accepted matches.
  - `ZSTD_ldm_generateSequences` chunks large input, performs overflow correction, enforces maximum distance, and carries leftover literals between chunks.
  - `ZSTD_ldm_reduceTable` adjusts table offsets after overflow correction.
- Sequence consumption:
  - `ZSTD_ldm_skipSequences` advances a raw sequence store when data is skipped.
  - `maybeSplitSequence` splits long raw sequences across block boundaries.
  - `ZSTD_ldm_blockCompress` compresses literal gaps with the normal block compressor and injects LDM matches into `seqStore_t`.

## Integration Points

This file is called by `zstd_compress.c` when LDM is enabled. It uses rolling-hash helpers, Zstd window maintenance, `ZSTD_selectBlockCompressor`, `ZSTD_storeSeq`, fast-table preload helpers, and normal strategy compressors.

## Notes

- LDM is disabled by returning zero workspace/sequence capacity when `enableLdm` is false.
- The implementation is careful about dictionary invalidation on overflow correction.
- Raw sequence offsets must remain valid at the end of split sequences, so max-distance enforcement is done before sequence generation.
