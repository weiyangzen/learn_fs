# sources/storage-engines/wiredtiger/src/support/modify.c

## Purpose
`modify.c` packs, applies, and reconstructs WiredTiger modify operations. A modify represents byte-range replacements against a value, allowing updates to store deltas rather than full values. The file supports cursor API modify calls and reconstructs full values by rolling visible modify updates forward from a base value.

## Important APIs, Types, and Functions
`__wt_modify_idempotent` checks whether every modify entry replaces exactly as many bytes as it writes. `__wt_modify_pack` serializes an array of `WT_MODIFY` entries into a scratch `WT_ITEM`. `__wt_modify_apply_item` applies a packed modify to a `WT_ITEM`, using `__modify_fast_path`, `__modify_apply_no_overlap`, and `__modify_apply_one`. `__wt_modify_apply_api` is the cursor-facing path that packs entries, grows the cursor value buffer, and applies the modify. `__wt_modify_reconstruct_from_upd_list` rebuilds a full value from a modify update and earlier updates or on-page data.

## Control Flow
Packing writes the entry count, then fixed-size metadata triples, then entry data contiguously to reduce unaligned access. Applying removes the trailing NUL for string format `S`, tries an in-place fast path for same-size overwrites, detects sorted non-overlapping modifications for reverse single-pass construction, and otherwise applies entries one by one with padding, overwrite, shrink, or grow behavior. Reconstruction walks the update list from the current modify until it finds a full standard update or falls back to the on-page value, collects visible modify updates, grows the destination buffer to the computed maximum, and applies modifies from oldest to newest.

## State and Persistence Behavior
Packed modify buffers are transient scratch items or `WT_UPDATE` payloads. Applying mutates the supplied `WT_ITEM` buffer in memory and may grow it before modification. Reconstruction populates `WT_UPDATE_VALUE`, carrying time-window fields from the original modify and producing a standard full value. The persistent implication is indirect: modify updates stored in update chains or history can be reconstructed into full values for reads and reconciliation.

## Dependencies and Integration Points
The file depends on cursor internals, `WT_MODIFY_FOREACH` macros, update vectors, transaction visibility macros, prepared-update state, on-page value return, buffer growth helpers, value-format semantics, and statistics counters. It integrates with `WT_CURSOR::modify`, update-chain reads, reconciliation, checkpoint handling, and transaction isolation.

## Risks
Offsets are cumulative in API order, so sorted/non-overlap fast paths must preserve modify semantics exactly. Buffer sizing is guarded by `WT_ASSERT_ALWAYS`; bad max-size calculation would be memory unsafe in non-diagnostic paths. Read-uncommitted readers cannot safely reconstruct values when concurrent aborts may remove required base data, so the function returns rollback for that case. Prepared rollback races require special handling of locked/in-progress prepare states. Applying modifies over tombstones or missing full base values is invalid and protected by assertions and retry logic.

## Test Signals
Tests should cover idempotent and resizing modifies, append beyond end with padding, replacement larger/smaller/same-size, sorted non-overlap fast path, overlapping fallback path, string `S` trailing-NUL preservation, cursor API stats increments, reconstruction from full update and from on-page value, read-uncommitted rollback, prepared rollback races, overflow item retry, and missing base-update assertions. Fuzzing offset/size combinations is valuable because arithmetic and memmove boundaries are central risks.
