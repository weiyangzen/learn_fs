# sources/object-store/rustfs/crates/filemeta/src/metacache.rs

## Purpose

This module provides two related capabilities. First, it models and streams metacache entries used for object listing and metadata reconciliation across disks. Second, it implements a generic asynchronous TTL cache with stale-value and background-refresh options.

Metacache entries carry an object or prefix name plus raw XL metadata bytes and optional decoded `FileMeta`. Reconciliation logic chooses or synthesizes a usable entry under directory/object quorum constraints.

## Important APIs, Types, and Functions

- `MetadataResolutionParams` carries directory quorum, object quorum, requested version count, bucket name, strict flag, and candidate version streams.
- `MetaCacheEntry` stores `name`, raw `metadata`, optional decoded `cached: FileMeta`, and `reusable`. Key methods include `marshal_msg`, `is_dir`, `is_in_dir`, `is_object`, `is_object_dir`, `is_latest_delete_marker`, `to_fileinfo`, `file_info_versions`, `matches`, and `xl_meta`.
- `MetaCacheEntries(Vec<Option<MetaCacheEntry>>)` provides `resolve()` for quorum reconciliation and `first_found()`.
- `MetaCacheEntriesSorted` wraps entries with list id/reuse/last skipped state, exposes flattened entries, and supports `forward_past(marker)`.
- `MetacacheWriter<W>` writes a stream with `METACACHE_STREAM_VERSION`, then repeated bool/name/bin records, ending with a false bool.
- `MetacacheReader<R>` reads the stream incrementally from an `AsyncRead`, with `peek()`, `skip(size)`, and `read_all()`.
- `Cache<T>` is a generic async cache using `UpdateFn<T>`, `ttl`, `Opts`, `ArcSwapOption`, an atomic last-update timestamp, and an async mutex to coalesce refreshes.
- `Opts` controls `return_last_good` and `no_wait` behavior.

## Control Flow

`MetaCacheEntry::to_fileinfo()` special-cases directory placeholders, uses cached metadata when available, and otherwise calls `get_file_info()` on raw bytes. `is_latest_delete_marker()` prefers cached versions, then fast indexed metadata checks, then full `xl_meta()` parsing, treating parse errors as delete markers in some paths.

`MetaCacheEntry::matches()` compares two entries. It first orders by name, handles directory placeholders, decodes both `FileMeta` values, compares version counts and latest mod times, then compares version headers. In non-strict mode it can ignore signature differences for otherwise matching headers and prefers the newest sortable header.

`MetaCacheEntries::resolve()` scans candidates, counts directory hits and valid object metadata, populates candidate version streams, chooses an initial or preferred selected entry, and returns directory entries if directory quorum is met. For objects, it rejects if valid object count is below quorum. If all valid objects agree, it reuses the selected entry. If they disagree, it calls `merge_file_meta_versions()`, marshals a new `FileMeta`, and returns a reusable synthetic `MetaCacheEntry`.

The stream writer lazily writes the version in `init()`, flushes after each object, and emits an end marker in `close()`. The reader lazily checks version, reads msgpack markers manually, buffers exact bytes as needed, and resets its buffer after each entry.

`Cache::get_shared()` returns fresh cached values when TTL has not expired. In `no_wait` mode, if the value is stale but less than twice TTL old, it returns the stale value and tries to spawn one background update. Otherwise it waits on the update mutex, rechecks freshness, runs `update()`, and returns the stored value. `return_last_good` suppresses update errors when a cached value exists.

## State and Persistence Behavior

Metacache entry persistence is a simple msgpack stream: version byte, then repeated records containing a boolean continuation marker, a string name, and binary metadata. The stream version currently written is `2`; the reader accepts versions `1` and `2`.

`MetaCacheEntry.cached` is an in-memory decode cache skipped by serde. `xl_meta()` populates it lazily. Reconciled entries may have `reusable=true` and newly marshaled metadata bytes reflecting merged versions.

The generic `Cache<T>` stores an `Arc<T>` in `ArcSwapOption`, records update time as Unix seconds, and uses a mutex only for update coordination. It does not persist across process restarts.

## Dependencies and Integration Points

Metacache integrates with `FileMeta`, `FileMetaShallowVersion`, `VersionType`, `get_file_info`, `FileInfoVersions`, `FileInfoOpts`, and `merge_file_meta_versions` from the filemeta crate. It uses `tokio` async IO/spawn/mutex, `rmp` marker decoding, `arc_swap` for lock-free cached reads, `time::OffsetDateTime`, and `tracing`.

It is likely used by object listing, quorum reads, healing/reconciliation, and cache-heavy metadata paths where repeatedly loading XL metadata would be expensive.

## Risks and Edge Cases

- `MetacacheReader::check_init()` reads two bytes and then decodes a `u8`; this may consume more than a single version byte depending on the stream and should be treated carefully if stream layout changes.
- `MetacacheReader::skip()` subtracts one when `current.is_some()`; calling it with `size == 0` while current is set would underflow `usize`.
- `read_more()` grows buffers based on caller-provided lengths from msgpack markers; malformed streams can request large allocations.
- `resolve()` clones entries and metadata extensively. Large listings or many versions can be allocation-heavy.
- `matches()` returns `(None, false)` on decode failures, which may cause reconciliation to drop candidates without surfacing detailed corruption signals.
- In the generic cache, future last-update timestamps intentionally force refresh via checked subtraction returning `u64::MAX`. System clock jumps can therefore trigger refreshes.
- `no_wait` returns stale values for up to `2 * ttl`; callers must opt in only where stale data is acceptable.

## Test Signals

Tests cover writer/reader round-tripping, rebuilding resolved metadata from merged versions, concurrent cache access, fresh `get_shared()` pointer reuse, future timestamp refresh behavior, `no_wait` background refresh behavior, background refresh coalescing, and `return_last_good` error handling both enabled and disabled.
