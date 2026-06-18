# sources/user-network-fs/gcsfuse/internal/cache/data/byte_range_map_test.go

## Purpose
This file tests chunk-level sparse range tracking in `ByteRangeMap`. It documents the core behavior that any partial range marks full chunks, cache coverage is all-or-nothing per chunk, and total bytes are accounted by chunk sizes.

## Important APIs, Types, And Functions
Tests cover `AddRange`, `ContainsRange`, `GetMissingChunks`, `TotalBytes`, `Clear`, `Chunks`, and the private `chunkSizeOf`. The test constant `MB` mirrors the default 1 MiB chunk size.

## Control Flow And State
`TestByteRangeMap_AddRange` is table driven and verifies empty maps, partial chunks, non-overlapping additions, repeated additions, spanning ranges, gap filling, overlap, and invalid ranges. Contains/missing tests build a sparse set of chunks 0, 2, and 5 and query covered, missing, and gapped ranges.

Total-byte tests verify idempotent additions, gap filling, and partial last-chunk accounting. Clear resets map and bytes. `TestByteRangeMap_ConcurrentAccess` runs one writer and one reader goroutine to exercise the locking contract. Chunk alignment tests assert partial range additions mark the entire chunk as present while adjacent chunks remain missing.

## State And Persistence Behavior
The suite uses only in-memory maps. State assertions observe downloaded chunk ids and `totalBytes`.

## Dependencies And Integration Points
The file uses `testing` and `testify/assert`. It does not involve file cache jobs or disk I/O, but it establishes behavior relied on by sparse cache file metadata.

## Risks And Edge Cases
The tests make the coarse chunk contract explicit: a 100-byte range marks a 1 MiB chunk. They do not cover very large chunk ids, ranges beyond file size in `AddRange`, or race-detector assertions beyond "run with -race" suitability.

## Test Signals
The suite is focused and high signal for `ByteRangeMap` semantics. It should catch accidental changes from chunk-granular to byte-granular accounting.
