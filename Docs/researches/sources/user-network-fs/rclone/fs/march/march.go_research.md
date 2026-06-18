# sources/user-network-fs/rclone/fs/march/march.go

## Purpose
`march.go` traverses source and destination filesystems in lock step. It is the matching engine used by sync-like operations to classify entries as source-only, destination-only, or matched, with support for filters, fast-list, no-traverse, depth limits, case-insensitive comparison, Unicode normalization, and concurrent directory processing.

## Important APIs, types, and functions
Core APIs are `March`, `Marcher`, and `March.Run`. `Marcher` callbacks are `SrcOnly`, `DstOnly`, and `Match`. Important internals include `init`, `srcOrDstKey`, `makeListDir`, `listDirJob`, `matchListings`, and `processJob`. `matchTransformFn` and `listDirFn` customize matching and listing.

## Control flow
`Run` initializes list functions and transforms, computes source/destination depth, starts checker worker goroutines, queues the root job, and waits for traversal completion. `processJob` lists source and destination directories concurrently or, in no-traverse mode, probes destination objects by name for each source object. `matchListings` merges sorted streams, skips duplicates, validates order, and dispatches callbacks. Callback return values enqueue child-directory jobs when depth allows.

## State and persistence behavior
`March` holds runtime listing functions, transforms, a semaphore limiting destination `NewObject` probes, and traversal queues. It does not directly mutate remotes; callback implementations perform sync/delete/copy behavior. It updates error counts through `fs.CountError` when listing fails.

## Dependencies and integration points
It integrates `fs.Fs`, `fs.DirEntry`, filters, `list.DirSortedFn`, `walk.NewDirTree` for fast-list/files-from no-traverse modes, `dirtree`, transform rules, `semaphore`, Unicode NFC normalization, and config fields such as `Checkers`, `UseListR`, `NoTraverse`, `MaxDepth`, `IgnoreCaseSync`, and `DeleteExcluded`.

## Risks and edge cases
Concurrency is subtle: job queue accounting, context cancellation, background no-traverse probes, and channel closure must avoid deadlocks. Duplicate handling depends on stable sorting and transformed keys. Directories sort before files by suffix. `NoCheckDest` treats destination as absent. If destination listings fail with `ErrorDirNotFound`, source items are copied anyway.

## Test signals
`march_test.go` covers source-only, identical, typical sync, no-traverse, fast-list, duplicate entries, case-insensitive matching, Unicode normalization, file-versus-directory distinctions, and local backend monkey-patched ListR behavior.

Source-read signal: reviewed complete local file (556 lines). Types observed: `matchTransformFn`, `listDirFn`, `March`, `Marcher`, `listDirJob`, `matchTask`. Functions/methods observed: `init`, `srcOrDstKey`, `srcKey`, `dstKey`, `makeListDir`, `Run`, `aborting`, `matchListings`, `processJob`.
