# sources/storage-engines/rocksdb/db/seqno_to_time_mapping.cc

## Purpose

`seqno_to_time_mapping.cc` implements the sampled sequence-number to wall-clock time map declared in `seqno_to_time_mapping.h`, plus small packing helpers used by timed value paths. The mapping gives RocksDB a compact, approximate bridge from write sequence numbers to Unix seconds for time-aware tiering and retention decisions. It is intentionally lossy: entries are sampled, merged, pruned by time span, and compacted by capacity.

## Important APIs, Types, and Functions

Key implementation functions are `FindGreaterTime`, `FindGreaterEqSeqno`, `FindGreaterSeqno`, `GetProximalTimeBeforeSeqno`, `GetProximalSeqnoBeforeTime`, and `GetCurrentTieringCutoffSeqnos`. Mutating paths include `Append`, `PrePopulate`, `AddUnenforced`, `DecodeFrom`, `CopyFromSeqnoRange`, `SetMaxTimeSpan`, `SetCapacity`, and `Enforce`. `SeqnoTimePair::Merge`, `Encode`, `Decode`, `ComputeDelta`, and `ApplyDelta` define pair-level compaction and persistence encoding. `PackValueAndWriteTime`, `PackValueAndSeqno`, and the parse helpers append or strip fixed-width trailers from value slices.

## Control Flow

Reads assume `enforced_` is true and use binary search over `pairs_`. `Append` tries to merge with the newest entry, handles clock/time anomalies through `SeqnoTimePair::Merge`, sorts only after unenforced additions, then enforces time-span and non-strict capacity limits. `Enforce` sorts/merges if necessary, prunes by `max_time_span_`, and strictly reduces to configured capacity. Capacity enforcement greedily removes interior entries whose removal creates the smallest time gap, preserving the endpoints. Decode appends decoded delta entries and rolls back on corruption; if it merges with an already constrained map it leaves the object unenforced until a later enforcement pass.

## State and Persistence Behavior

Persistent representation is varint count followed by delta-encoded varint sequence/time pairs; an empty map encodes as an empty string. The map keeps one older-than-cutoff entry so queries near the retention boundary still have a lower bound. Sequence number zero and time zero are reserved unknown-before-all sentinels and are skipped or asserted around. Packed timed values persist a fixed 64-bit trailer after the user value, so callers must pass slices of at least eight bytes to parse.

## Dependencies and Integration Points

The file depends on `db/dbformat.h`, `db/version_edit.h`, and string/coding utilities. `ColumnFamilyData`, `SuperVersion`, table properties, and tiering options consume these mappings to estimate sequence cutoffs for `preserve_internal_time_seconds` and `preclude_last_level_data_seconds`. SST metadata can carry copied sequence ranges through `EncodeTo`/`DecodeFrom`.

## Risks and Test Signals

Risks center on sortedness/enforcement preconditions, off-by-one cutoff semantics, unsigned underflow in time-span pruning, corruption rollback, and fixed-trailer parsing asserts. Tests should cover duplicate seqnos, duplicate times, backward time movement, capacity zero/one, strict versus non-strict compaction, decode corruption with rollback, range copy boundary inclusion, tiering cutoff `+1`, and packed value round trips.
