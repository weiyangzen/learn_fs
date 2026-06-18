# sources/sync-backup/kopia/repo/ecc/ecc_utils.go

## Purpose
Provides small numeric and slice utilities used by ECC sizing and buffer preparation.

## Important APIs, Types, And Functions
Functions are `computeShards`, `between`, `applyPercent`, `fillWithZeros`, `minInt`, `maxInt`, `maxFloat32`, and `ceilInt`.

## Control Flow
`computeShards` starts from 128 data shards, derives parity shards from the overhead percentage, clamps to 1..128, and if that would produce one parity shard, switches to two parity shards and computes the data-shard count instead. Other helpers are simple arithmetic or loops.

## State And Persistence
No state or persistence. `fillWithZeros` mutates the provided byte slice.

## Dependencies And Integration Points
Depends on `math`. Used heavily by `ecc_rs_crc.go` for shard count, shard size, block count, and zero padding.

## Risks And Edge Cases
Very low overhead percentages can produce high data-shard counts with two parity shards. `applyPercent` floors rather than rounds, which affects parity capacity. Division helpers assume positive denominators.

## Test Signals
`ecc_utils_test.go` checks representative shard-count outputs and uses the helpers through ECC round-trip tests.
