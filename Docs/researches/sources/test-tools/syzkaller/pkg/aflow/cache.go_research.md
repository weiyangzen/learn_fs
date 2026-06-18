# sources/test-tools/syzkaller/pkg/aflow/cache.go

## Purpose

`cache.go` implements aflow's on-disk cache for expensive workflow artifacts such as kernel checkouts, builds, LLM responses, and serialized execution objects. It provides reference-counted cache entry use, metadata-based startup recovery, temporary directories, and size-based purging.

## Important APIs, Types, and Functions

`Cache` stores root dir, max size, time source, mutex, current size, and `entries`. `cacheEntry` tracks dir, size, usage count, and last use. `NewCache` and `newTestCache` initialize from disk. `Create` creates or returns a cache dir for `(typ, desc)`. `cacheCreateObject` and `cacheReadObject` store/load JSON objects. `Release`, `TempDir`, `init`, and `purge` manage lifecycle. Metadata is `cacheMeta` in `aflow-meta`, currently version `1`.

## Control Flow

Initialization scans `dir/*/*`, removes incomplete directories with no metadata, upgrades stale metadata by recomputing disk usage, loads entries, and purges if needed. `Create` locks, hashes `desc` into an entry ID, removes any stale incomplete target dir, populates the final directory, writes metadata after successful population, increments usage, updates metadata mtime, and purges old unused entries. `purge` sorts entries by usage count then last-used time and deletes oldest unused entries until below max size.

## State and Persistence Behavior

Cache state persists on disk under type/hash directories. Validity is marked by the `aflow-meta` file, not by atomic rename, because kernel build paths may be embedded in artifacts. Temporary directories are placed under `tmp` without metadata and are cleaned on next cache init or by `Context.Close`.

## Dependencies and Integration Points

It depends on `hash.String`, `osutil` filesystem helpers, JSON helpers, and disk usage. `execute.go` wraps it through `Context.Cache`, `CacheObject`, `RetrieveObject`, and `TempDir`. Kernel, repro, LLM, and patch-test actions all depend on this cache.

## Risks and Edge Cases

Callers must call `Release` exactly once per successful `Create`; missing releases prevent purging, while double releases panic. Failed `populate` removes the directory. Because creation happens directly in the final path, readers must rely on metadata existence to distinguish complete entries. `purge` requires the mutex to already be locked and panics if not. `currentSize < maxSize` means a cache exactly at max size will attempt purge.

## Test Signals

Tests cover cache hit/miss behavior, failed population cleanup, restart recovery, incomplete-dir cleanup, max-size purging by last use, JSON object storage, cache object retrieval, and invalid cached ID validation through the public context helper.
