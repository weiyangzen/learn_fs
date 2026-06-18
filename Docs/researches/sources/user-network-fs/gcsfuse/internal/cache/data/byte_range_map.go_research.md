# sources/user-network-fs/gcsfuse/internal/cache/data/byte_range_map.go

## Purpose
`ByteRangeMap` tracks downloaded chunks for sparse file cache mode. It records chunk presence rather than exact byte ranges, allowing cache reads to determine whether requested ranges are fully backed locally and how many bytes should count toward cache occupancy.

## Important APIs, Types, And Functions
`DefaultChunkSize` is 1 MiB. `ByteRangeMap` stores a mutex, chunk size, total file size, a `map[uint64]bool` of downloaded chunk ids, and `totalBytes`. Public methods are `NewByteRangeMap`, `AddRange`, `ContainsRange`, `GetMissingChunks`, `TotalBytes`, `Clear`, and `Chunks`. Private helpers are `chunkID` and `chunkSizeOf`.

## Control Flow And State
`NewByteRangeMap` normalizes a zero chunk size to the default. `AddRange` locks for writing, treats empty or inverted ranges as no-op, maps `[start,end)` to inclusive chunk ids, marks any previously absent chunks, and increments `totalBytes` by each new chunk's physical size. `chunkSizeOf` accounts for the final partial chunk and returns zero for chunks starting beyond file size.

`ContainsRange` and `GetMissingChunks` use read locks and the same chunk-id conversion. Empty ranges are considered contained and have no missing chunks. `Chunks` returns a sorted list of downloaded ids for debugging and tests.

## State And Persistence Behavior
All state is in memory and protected by `sync.RWMutex`. The map is coarse-grained: adding a partial byte range marks the whole containing chunk downloaded. `totalBytes` is a sum of chunk sizes, not requested byte counts.

## Dependencies And Integration Points
The file depends only on the standard library `slices` and `sync`. It is embedded in `data.FileInfo` for sparse cache mode and initialized by `CacheHandler` with the downloader chunk size.

## Risks And Edge Cases
Callers must ensure actual downloads align with the chunk size; otherwise `ContainsRange` may claim local coverage for bytes not really downloaded. Ranges beyond file size can mark out-of-bounds chunk ids but add zero bytes for fully beyond-end chunks. The design is intentionally chunk-level and not suitable for exact sub-chunk coverage.

## Test Signals
`byte_range_map_test.go` covers partial chunks, overlaps, gaps, empty ranges, total byte accounting including partial final chunks, clearing, sorted chunk lists, chunk-size helper behavior, and basic concurrent access.
