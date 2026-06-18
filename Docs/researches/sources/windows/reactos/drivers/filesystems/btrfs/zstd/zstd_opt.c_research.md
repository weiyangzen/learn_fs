# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_opt.c

## Scope And Purpose

`zstd_opt.c` implements Zstd's optimal parser strategies: `btopt`, `btultra`, and `btultra2`. It builds a binary-tree match finder, prices literals/matches from adaptive statistics, computes a shortest path through candidate sequences, and emits the chosen parse.

Complete file read: 1200 lines.

## Main Components

- Price model:
  - `ZSTD_bitWeight`, `ZSTD_fracWeight`, and `WEIGHT` convert symbol frequencies to bit-cost estimates.
  - `ZSTD_rescaleFreqs` initializes or decays literal, literal-length, match-length, and offset-code statistics, optionally from dictionary entropy tables.
  - `ZSTD_rawLiteralsCost`, `ZSTD_litLengthPrice`, and `ZSTD_getMatchPrice` score candidate sequences.
  - `ZSTD_updateStats` updates adaptive statistics after emitting a sequence.
- Match insertion and collection:
  - `ZSTD_insertAndFindFirstIndexHash3` maintains the special 3-byte hash table.
  - `ZSTD_insertBt1` inserts positions into the binary tree.
  - `ZSTD_updateTree_internal` and exported `ZSTD_updateTree` advance the tree for dictionary loading.
  - `ZSTD_insertBtAndGetAllMatches` collects repcode, hash3, binary-tree, external-dictionary, and dictionary-match-state candidates.
  - `ZSTD_BtGetAllMatches` dispatches match collection by `minMatch`.
- Optimal parsing:
  - `ZSTD_compressBlock_opt_generic` initializes costs, explores candidate parses in `priceTable`, updates per-position repcodes, backtracks the lowest-cost path, emits sequences, and returns last-literal length.
- Public wrappers:
  - `ZSTD_compressBlock_btopt`
  - `ZSTD_compressBlock_btultra`
  - `ZSTD_compressBlock_btultra2`
  - Dictionary-match-state and external-dictionary variants for btopt/btultra.
- Two-pass ultra mode:
  - `ZSTD_initStats_ultra` performs a first pass on the first block to seed statistics, then resets match history before the real parse.
  - `ZSTD_upscaleStats` reinforces first-pass statistics.

## Integration Points

The file is selected by `zstd_compress.c` for high compression strategies. It depends on `hist.h`, FSE/HUF symbol-cost state, `ZSTD_storeSeq`, repcode update helpers, binary-tree tables in `ZSTD_matchState_t`, and the shared constants in `zstd_internal.h`.

## Notes

- `btultra2` is intentionally first-block/no-dictionary/no-LDM only.
- The parser uses bounded tables sized by `ZSTD_OPT_NUM`; large matches can trigger immediate encoding.
- Cost model changes directly affect compression ratio, speed, and decompression locality.
