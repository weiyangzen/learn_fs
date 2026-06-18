# sources/user-network-fs/s3fs-fuse/src/fdcache_untreated.h

## Purpose
Declares the `UntreatedParts` range-tracking class used by s3fs-fuse cache code to manage byte ranges that are pending treatment. It presents a small synchronized API for adding, selecting, clearing, replacing, removing, duplicating, and dumping dirty ranges.

## Important APIs, Types, And Functions
`UntreatedParts` owns a `mutable std::mutex untreated_list_lock`, an `untreated_list_t untreated_list`, and a `long last_tag`. Copy and move are deleted to avoid unsafe mutex/vector transfer. Public API includes `empty()`, `AddPart()`, `GetLastUpdatedPart()`, `ClearParts()`, `ClearAll()`, `GetLastUpdatePart()`, `ReplaceLastUpdatePart()`, `RemoveLastUpdatePart()`, `Duplicate()`, and `Dump()`. `GetLastUpdatedPart()` is an inline wrapper around private `RowGetPart()` and defaults `min_size` to `MIN_MULTIPART_SIZE`, making the class directly aware of multipart upload sizing.

## Control Flow
The header exposes a lock-protected, non-copyable object with inline adapters for common operations. Selection of ranges flows through `RowGetPart(start, size, max_size, min_size, lastpart)`, with the header only exposing the `lastpart=true` path as `GetLastUpdatedPart()`. `ClearAll()` delegates to `ClearParts(0, 0)`, following the implementation convention that zero size clears from the start position to the end.

## State And Persistence Behavior
All state is in memory. `untreated_list` is annotated with `GUARDED_BY(untreated_list_lock)` and stores vector entries from `types.h`. `last_tag` identifies the latest updated range; it starts at zero and is incremented by adds in the `.cpp`. There is no serialization or external persistence contract.

## Dependencies And Integration Points
The header depends on `common.h` for thread-safety annotations/constants and on `types.h` for `untreated_list_t`. It is included by fd-cache implementation files that need to track pending byte ranges for writeback and multipart upload decisions. The default `MIN_MULTIPART_SIZE` ties callers to S3 multipart constraints unless they override `min_size`.

## Risks
The public name pair `GetLastUpdatedPart()` and `GetLastUpdatePart()` is easy to confuse: the former applies min/max chunk sizing through `RowGetPart()`, while the latter returns the whole last-tagged part. Because only a latest-update selector is exposed, callers that need global dirty-range ordering must rely on `Duplicate()`. Header-level thread annotations help static analysis only if the build enables compatible tooling.

## Test Signals
Compile tests should ensure non-copyability, default construction, and access through inline methods. Behavioral tests belong mostly to `fdcache_untreated.cpp` but should explicitly validate the differing semantics of `GetLastUpdatedPart()` versus `GetLastUpdatePart()` and the `ClearAll()` zero-size convention.
