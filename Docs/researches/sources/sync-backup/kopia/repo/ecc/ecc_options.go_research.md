# sources/sync-backup/kopia/repo/ecc/ecc_options.go

## Purpose
Defines configuration for ECC algorithms.

## Important APIs, Types, And Functions
`Options` includes `Algorithm`, `OverheadPercent`, `MaxShardSize`, and `DeleteFirstShardForTests`. `DefaultAlgorithm` is `AlgorithmReedSolomonWithCrc32`.

## Control Flow
No functions are defined. Other ECC code reads these fields to select algorithms and tune shard layout.

## State And Persistence
Options are serializable via JSON tags, allowing repository format or blob-provider settings to persist ECC choices.

## Dependencies And Integration Points
Used by `CreateAlgorithm` and `newReedSolomonCrcECC`. The testing-only flag is consumed by the Reed-Solomon decrypt path to simulate data loss.

## Risks And Edge Cases
Comments say overhead should be between 0 and 100, but validation is not in this file. A zero algorithm disables ECC at higher layers; a zero max shard size triggers automatic selection in the implementation.

## Test Signals
Behavior of options is covered through Reed-Solomon tests with explicit overhead and shard sizes.
