# sources/user-network-fs/s3fs-fuse/src/fdcache_untreated.cpp

## Purpose
Implements `UntreatedParts`, the mutable range tracker used by the file descriptor cache to remember byte ranges that still need follow-up treatment, typically upload or multipart synchronization. The implementation keeps ranges ordered, merges adjacent or overlapping intervals, tags the most recent update, and lets callers clear or replace tracked ranges after work is completed.

## Important APIs, Types, And Functions
The public methods are declared in `fdcache_untreated.h`; this file supplies their behavior. `empty()` reports whether the protected `untreated_list_t` is empty. `AddPart(start, size)` validates a positive range, increments `last_tag`, and either stretches an existing `untreatedpart`, inserts before the first later range, or appends a new range. `RowGetPart()` is the private selector behind `GetLastUpdatedPart()`, returning the most recent tagged range when it is at least `min_size`, capped by `max_size`. `ClearParts(start, size)` removes a byte span, with `size == 0` meaning clear everything from `start` onward. `GetLastUpdatePart()`, `ReplaceLastUpdatePart()`, and `RemoveLastUpdatePart()` operate on the currently `last_tag`-marked range. `Duplicate()` snapshots the vector, and `Dump()` logs the range list.

## Control Flow
All methods take `untreated_list_lock` before touching the vector or tag. `AddPart()` walks the list once. On overlap or adjacency, `untreatedpart::stretch()` widens the current interval and applies the new tag, then the implementation keeps stretching across following intervals until the next range no longer overlaps. Without overlap, the function inserts before the first interval whose start is greater than the new range end. `ClearParts()` also walks the vector, considering four cases: no more overlap, deletion/trimming at the start side, trimming or splitting when the clear span begins inside a range, and no overlap behind the current range. Last-update operations linearly scan for `untreated_tag == last_tag`.

## State And Persistence Behavior
State is process-local and in memory only: `untreated_list` stores `untreatedpart{start,size,untreated_tag}` entries and `last_tag` monotonically identifies the latest add or merged update. There is no disk persistence. `Duplicate()` is the escape hatch for callers needing an immutable copy outside the mutex. `Dump()` emits state to the s3fs logger but does not alter it.

## Dependencies And Integration Points
The code depends on `types.h` for `untreatedpart` and `untreated_list_t`, `common.h` constants via the header, and `s3fs_logger.h` for diagnostics. Its natural integration point is `FdEntity`/fdcache writeback logic: callers can mark dirty file ranges, request an upload-sized chunk via `GetLastUpdatedPart()`, and clear or adjust the range after multipart upload progress.

## Risks
`start + size` arithmetic is unchecked and can overflow `off_t` for extreme inputs, affecting ordering and overlap decisions. The split branch of `ClearParts()` mutates `iter->size` before computing `next_size` from `iter->start + iter->size`, so clearing a middle slice from a range can compute the tail length from the shortened front range rather than the original end; this is a concrete boundary-risk area for tests. The `last_tag` model assumes a single latest update is meaningful after merges; if merged ranges inherit the newest tag, older dirty spans can become hidden from `GetLastUpdatedPart(lastpart=true)` until additional calls clear/replace the latest range. `Dump()` logs `{start - size}` rather than `{start - end}`, which may confuse debugging.

## Test Signals
Useful tests should cover adding adjacent intervals, overlapping intervals, insertion before/after, `GetLastUpdatedPart()` with min/max thresholds, clearing prefixes/suffixes/whole ranges, clearing with `size == 0`, and splitting a range in the middle. Concurrency tests can verify `Duplicate()` snapshots are consistent while multiple threads add/clear. Boundary tests should exercise zero/negative inputs, maximum `off_t`-adjacent ranges, and the suspected `ClearParts()` split arithmetic.
