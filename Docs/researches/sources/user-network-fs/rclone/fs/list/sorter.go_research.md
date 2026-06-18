# sources/user-network-fs/rclone/fs/list/sorter.go

## Purpose
`sorter.go` provides a scalable sorter for directory entries. It sorts in memory for small lists and switches to on-disk external sorting above `--list-cutoff`, then streams sorted entries back through a `ListR`-style callback.

## Important APIs, types, and functions
Exports are `NewObjecter`, `Sorter`, `KeyFn`, `NewSorter`, `Sorter.Add`, `Sorter.Send`, `Sorter.CleanUp`, and `SortToChan`. Important internals are `entryToKey`, `keyToEntry`, `startExtSort`, `sendEntriesToExtSort`, and the `listHelper` that batches rehydration from external-sort keys.

## Control flow
`NewSorter` captures config, context cancellation, callback, and key function. `Add` appends entries until cutoff, then initializes `extsort.Strings`, sends accumulated entries as `key + NUL + remote`, and streams later additions to the sorter. `Send` either stable-sorts the in-memory slice or closes the external-sort input, reads sorted keys, recreates directory entries directly and objects via `NewObject`, batches callbacks, and returns accumulated rehydration errors. `CleanUp` cancels background work and clears memory.

## State and persistence behavior
Small sort state is in-memory. External sort state includes channels, an `extsort.StringSorter`, temporary files in OS temp or `tempDir`, cancellation state, and error aggregation. No source/destination filesystem data is mutated, but external mode reopens objects by remote.

## Dependencies and integration points
The sorter depends on `lanrat/extsort`, `errcount`, `errgroup`, rclone `fs.DirEntry`, `fs.Object`, `fs.Directory`, and config `ListCutoff`/`Checkers`. It is used by `DirSortedFn` and by `march` tests to produce sorted channels.

## Risks and edge cases
External mode only serializes remote names, so objects must still exist and be resolvable by `NewObject` during `Send`. Directory entries are reconstructed minimally with zero modtime. Keys use NUL as a separator. Temp-file initialization can fail and must return an error rather than panic. Concurrent `Add` calls are mutex-protected, but callbacks run under `Send`.

## Test signals
`sorter_test.go` validates identity and custom-key sorting, external switch thresholds, object/directory rehydration, 100k-entry boundary behavior, temp-directory failure handling for issue-style regressions, cleanup, and a large benchmark for 10 million entries.

Source-read signal: reviewed complete local file (354 lines). Types observed: `NewObjecter`, `Sorter`, `KeyFn`, `listHelper`. Functions/methods observed: `identityKeyFn`, `NewSorter`, `entryToKey`, `keyToEntry`, `sendEntriesToExtSort`, `startExtSort`, `Add`, `newListHelper`, `send`, `Add`, `Flush`, `Send`, `CleanUp`, `SortToChan`.
