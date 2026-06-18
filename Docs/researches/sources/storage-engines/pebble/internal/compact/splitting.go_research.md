# sources/storage-engines/pebble/internal/compact/splitting.go

## Purpose
This file implements compaction output splitting and a generic frontier heap used to notify components when iteration advances past key boundaries.

## Important APIs, Types, And Functions
`ShouldSplit` is `NoSplit` or `SplitNow`. `OutputSplitter` tracks start key, limit, target size, grandparent boundaries, frontier state, and split key. Key methods are `NewOutputSplitter`, `ShouldSplitBefore`, `SplitKey`, `boundaryReached`, `setNextBoundary`, and `shouldSplitBasedOnSize`. `frontier`, `frontierReachedFn`, and `Frontiers` implement registered key-boundary callbacks with `Init`, `Update`, `Advance`, and heap operations.

## Control Flow
The splitter finds grandparent file boundaries after the output start, registers a frontier, and on each candidate key checks whether a hard limit or grandparent boundary was reached. It splits near grandparent boundaries when estimated size is between 0.5x and 2x target, splits immediately at 2x, and splits by size after exhausting boundaries. It uses `equalPrevFn` to avoid splitting a user key across tables.

## State And Persistence Behavior
State is transient per output table but determines durable SST boundaries and future write amplification. `SplitKey` unregisters the frontier and returns either the selected split or the configured limit.

## Dependencies And Integration Points
It depends on `manifest.LevelIterator`, `base.Compare`, and `Frontiers` advanced by `compact.Iter`. `Runner` instantiates it while writing tables.

## Risks And Edge Cases
Risks include boundary/frontier drift, splitting at or before start key, splitting inside a user key, too-small outputs, too-large outputs, and grandparent heuristic thresholds that are inherited but not deeply principled.

## Test Signals
`splitting_test.go` validates output splitter choices and frontier heap behavior through datadriven fixtures, including randomized first-key frontier advancement.
