# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_double_fast.c

## Summary
Implements zstd's double-fast compression match finder, which maintains both small-min-match and 8-byte hash tables to find quick short and long matches.

## Key APIs
- `ZSTD_fillDoubleHashTable()`.
- `ZSTD_compressBlock_doubleFast()`.
- `ZSTD_compressBlock_doubleFast_dictMatchState()`.
- `ZSTD_compressBlock_doubleFast_extDict()`.

## Important Behavior
`ZSTD_fillDoubleHashTable()` primes the large and small hash tables from prior input, with full or fast dictionary table loading. The generic no-dictionary/dictMatchState compressor checks repeat codes, long hash matches, then short hash matches, with a +1 long-match probe after short hits. Matches are extended backward to the anchor where possible, stored with `ZSTD_storeSeq()`, and followed by complementary insertions plus immediate repcode checks.

The dictMatchState path searches an attached dictionary's hash tables while translating dictionary indexes into current-window offsets. The extDict variant handles a split dictionary/prefix window and falls back to the regular variant when the external dictionary has been invalidated by distance limits. Public wrappers specialize by `minMatch` values 4 through 7.

## Risks
Correctness depends on window limits, dictionary index deltas, and repcode validation. The code intentionally uses unsigned underflow tests for range checks and assumes dictionary match states are attached and within the active window when selected.
