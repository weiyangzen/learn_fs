# sources/user-network-fs/rclone/fs/list/helpers.go

## Purpose
`helpers.go` contains small listing utilities for backend implementations. It batches `ListR` callback entries and adapts backends that implement `ListP` into the ordinary `List` style return.

## Important APIs, types, and functions
`Helper` stores a `fs.ListRCallback` and buffered `fs.DirEntries`. `NewHelper`, `Add`, `Flush`, and internal `send` implement 100-entry batching. `WithListP` calls a `fs.ListPer` backend and accumulates all paged callback entries into one `fs.DirEntries` slice.

## Control flow
Backends construct a `Helper` with their recursive-list callback, call `Add` for each entry, and call `Flush` at the end. `Add` ignores nil entries and triggers the callback when the buffer reaches 100 entries. `WithListP` appends each `ListP` callback page to a result slice while updating accounting stats.

## State and persistence behavior
State is transient per helper instance: a callback and in-memory entry buffer. There is no persistence. `WithListP` updates process accounting counters through the context's stats object.

## Dependencies and integration points
The file depends on `fs.ListRCallback`, `fs.DirEntries`, `fs.ListPer`, and `accounting.Stats`. It is used by backends implementing fast/recursive listing and by backends that expose paged listing but need a `List` adapter.

## Risks and edge cases
Callers must remember to `Flush`, or the final partial batch is lost. `WithListP` can hold all entries in memory, so it is not suitable for huge listings when a streaming callback is available. Callback errors stop processing and leave buffered state as-is.

## Test signals
`helpers_test.go` checks constructor state, nil entry handling, threshold sending at 100 entries, flush behavior, `WithListP` aggregation, and partial result return when the paged listing reports an error.

Source-read signal: reviewed complete local file (61 lines). Types observed: `Helper`. Functions/methods observed: `NewHelper`, `send`, `Add`, `Flush`, `WithListP`.
