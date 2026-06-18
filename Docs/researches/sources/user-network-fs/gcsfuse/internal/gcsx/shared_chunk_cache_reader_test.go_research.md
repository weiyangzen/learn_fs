# sources/user-network-fs/gcsfuse/internal/gcsx/shared_chunk_cache_reader_test.go

## Scope

This suite validates `SharedChunkCacheReader` using temporary cache directories and fake GCS buckets.

## Purpose

The tests protect on-demand chunk caching behavior, chunk-boundary reads, cache hits, concurrency, fallback conditions, and resilience to cache directory races.

## Important APIs, Types, And Functions

- `sharedChunkCacheReaderTest` sets up a temp cache dir, `SharedChunkCacheManager`, fake bucket, object data, and reader.
- Suite tests cover constructor, single and multi-chunk reads, cache hits, EOF/negative/partial/zero reads, and exclusion regex.
- Standalone tests cover concurrent reads, same-chunk race, deleted directory recovery, download permission failure, corrupted cached chunk, and GCS download failure.

## Control Flow

Tests create deterministic byte-pattern objects in a fake bucket, call `ReadAt` with offsets and buffers, and verify response sizes, buffer contents, chunk file existence, and error types. Failure tests manipulate filesystem permissions, truncate chunk files, or use missing fake-bucket objects.

## State And Persistence Behavior

The cache directory is `t.TempDir()` in all major tests, so chunk files are isolated. Tests inspect chunk paths derived from bucket name, object name, generation, and chunk index. Cache-hit behavior is verified by comparing chunk file modification time before and after the second read.

## Dependencies And Integration Points

It depends on `file.NewSharedChunkCacheManager`, `fake.NewFakeBucket`, `gcs.CreateObjectRequest`, metrics/tracing noops, `timeutil.RealClock`, testify suite/assert/require, and OS file operations.

## Risks And Maintenance Notes

Permission-denied behavior can vary when tests run with elevated privileges or unusual filesystems. The same-chunk race test asserts success for all goroutines and a final chunk file but does not prove only one remote download occurred. The tests validate fallback error types, not integration with read-manager fallback overwrite behavior.

## Test Signals

Signals include exact data equality for chunk reads, chunk files created for every needed chunk, modification time unchanged on cache hit, EOF at object size, negative offset error text, partial tail size of remaining bytes, `FallbackToAnotherReader` for exclusions and failures, successful concurrent reads, directory recreation after deletion, and corrupted chunk detection via short read.
