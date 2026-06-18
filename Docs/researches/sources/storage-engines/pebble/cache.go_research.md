<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cache.go -->
# sources/storage-engines/pebble/cache.go

## Purpose
Exports Pebble's internal block-cache type and constructor as the public `pebble.Cache` API.

## Important APIs, Types, and Functions
`type Cache = cache.Cache` is a type alias, not a wrapper, so all methods and reference-count semantics of `internal/cache.Cache` are exposed directly. `NewCache(size int64) *cache.Cache` calls `cache.New(size)`.

## Control Flow
There is no internal control flow beyond constructing the cache. The comments describe the intended lifecycle: create the cache, pass it into one or more DBs, and usually release the creator's reference with `Unref` after DB creation.

## State and Persistence Behavior
The cache is process memory only. It allocates memory on demand and starts with reference count 1. DBs that use it add their own references. No filesystem state is persisted.

## Dependencies and Integration Points
The file depends only on `github.com/cockroachdb/pebble/internal/cache`. Integration points are `Options.Cache`, tests that create block-cache handles, file-cache reader setup, and all SSTable/block reading paths that use Pebble's shared block cache.

## Risks and Edge Cases
Mismanaging references can leak cache memory or prematurely release it while DBs still rely on it. Because this is an alias, changes to the internal cache API surface through the public Pebble package. A zero or very small size is delegated to internal cache behavior.

## Test Signals
No direct tests live in this file. Indirect coverage appears throughout Pebble tests that call `NewCache`, create cache handles, and unref them, including blob rewrite tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cache.go -->
