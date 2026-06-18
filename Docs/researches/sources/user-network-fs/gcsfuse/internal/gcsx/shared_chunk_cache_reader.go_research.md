# sources/user-network-fs/gcsfuse/internal/gcsx/shared_chunk_cache_reader.go

## Scope

This file implements `SharedChunkCacheReader`, a `gcsx.Reader` that serves reads from a shared on-disk chunk cache and downloads missing chunks on demand.

## Purpose

The reader supports shared-cache deployments, especially NFS-like environments, by avoiding whole-file prefetch and instead caching only chunks needed by reads. It falls back to the next reader when cache operations or chunk downloads fail.

## Important APIs, Types, And Functions

- `SharedChunkCacheReader` stores a shared chunk cache manager, bucket, object metadata, metrics/tracing handles, and FUSE handle ID.
- `NewSharedChunkCacheReader` constructs the reader.
- `ReadAt` checks exclusion/bounds, reads across chunk boundaries, opens cached chunks directly, downloads missing chunks, fills the caller buffer, and returns `ReadResponse`.
- `downloadChunk` creates temporary chunk files, downloads from GCS range reads, closes/syncs, and atomically renames to final chunk path.
- `ReaderName`, `CheckInvariants`, and `Destroy` implement `Reader`.

## Control Flow

`ReadAt` returns fallback immediately for excluded objects. It validates offset, logs and starts metrics timing, then loops while the buffer has remaining bytes and the object has data. For each chunk it computes chunk index and byte limits, tries `os.Open`, downloads on `ENOENT`, reopens the chunk, reads the requested slice with `ReadAt`, and advances counters. Non-ENOENT open errors, download errors, incomplete reads, and corrupted chunks return `FallbackToAnotherReader`.

## State And Persistence Behavior

The reader itself is stateless between reads. Persistent state lives in chunk files under manager-derived object/generation directories. Downloads use unique temporary paths, write the full chunk, close the file, and `os.Rename` atomically to the final chunk path. Directory recreation handles one LRU eviction race. `Destroy` is a no-op.

## Dependencies And Integration Points

It depends on `file.SharedChunkCacheManager`, GCS bucket range reads, metrics file-cache counters, logging, UUID request IDs, OS file APIs, syscall errno checks, and FUSE handle IDs. `read_manager.go` installs it before other readers when a shared chunk cache manager is configured.

## Risks And Maintenance Notes

Concurrent downloads of the same chunk can race at rename time; one may fail and fall back, depending on temp-path and final rename behavior. `defer chunkFile.Close()` inside the loop defers all closes until the full read returns, which is simple but can hold multiple descriptors for large reads. Metrics classify offset zero as sequential and all others as random, not using `ReadInfo`. Partial data copied into the caller buffer before fallback is returned with response size zero, so fallback callers must overwrite or ignore partial buffer contents.

## Test Signals

`shared_chunk_cache_reader_test.go` covers construction, single-chunk read, cache hit without file modification, cross-boundary reads, EOF, negative offset, partial tail reads, regex exclusion fallback, full multi-chunk reads, zero-length reads, concurrent reads, same-chunk race behavior, deleted directory recovery, download failure fallback, corrupted cache fallback, and GCS read failure fallback.
