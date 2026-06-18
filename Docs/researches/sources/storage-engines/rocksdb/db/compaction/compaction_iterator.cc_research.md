# sources/storage-engines/rocksdb/db/compaction/compaction_iterator.cc

## Purpose

`compaction_iterator.cc` implements RocksDB's `CompactionIterator`, the forward-only iterator that transforms sorted internal key/value input into the records that should be written by a flush, compaction, or related table-file creation path. It applies compaction semantics across user-key versions: snapshot visibility, range tombstone masking, SingleDelete pairing, merge collapsing, compaction filters, user-defined timestamp history GC, sequence-number zeroing, blob value extraction, and blob garbage collection. It also implements `CompactionBlobResolver`, a lazy wide-column blob resolver used by newer compaction filter APIs.

The file is on a critical correctness path. It decides whether old versions, tombstones, blob references, merge operands, and timed puts are preserved, rewritten, or dropped. Any change can affect point lookup visibility, iterator results, transaction conflict detection, blob-file reachability, or crash-recovery observability.

## Important APIs, types, and functions

`CompactionBlobResolver::Init`, `Reset`, `ResolveColumn`, `IsBlobColumn`, and `NumColumns` provide lazy access to blob-backed columns inside a wide-column entity. `ResolveColumn` can return inline values directly, decode inlined blob values, or fetch blob bytes through `BlobFetcher` and optional `PrefetchBufferCollection`. It updates `CompactionIterationStats` for blob reads and can remember a sticky error for FilterV4 so compaction fails even if a filter notices the error and returns keep.

The two `CompactionIterator` constructors initialize the iterator and create a `RealCompaction` proxy when a real `Compaction` is provided. They wire `SequenceIterWrapper`, comparator, merge helper, snapshot state, range deletion aggregator, blob file builder, compaction filter, shutdown/manual cancellation signals, timestamp history configuration, optional blob fetcher, optional prefetch buffers, and blob GC cutoff state.

`SeekToFirst` starts the scan by calling `NextFromInput` and `PrepareOutput`. `Next` advances through merge-output sub-iterations first, otherwise advances the input iterator as needed, then repeats `NextFromInput` and `PrepareOutput`.

`InvokeFilterIfNeeded` applies `CompactionFilter` to committed value-like records. It handles value, blob index, and wide-column entity inputs; supports stacked BlobDB-specific internal filtering; fetches blob values for integrated BlobDB when required; deserializes wide-column entities; supports lazy FilterV4 blob resolution; translates filter decisions into delete, single delete, changed value, changed blob index, changed wide-column entity, skip-until seek, or failure.

`NextFromInput` is the core compaction state machine. It parses internal keys, tracks current user key and timestamp, checks commit visibility, applies filters, computes snapshot stripes, decides whether to keep/drop SingleDelete, regular deletion, merge, value, timed put, blob index, wide-column entity, or range deletion sentinel records, and propagates shutdown, manual pause, corruption, and input status.

`PrepareOutput` performs final output rewriting: large values become blob indexes, blob indexes may be relocated or inlined by blob GC, wide-column entities may have large columns extracted or blob columns GC'd, and bottommost compactions can zero sequence numbers and user timestamps when safe.

Blob helpers include `ExtractLargeValueIfNeededImpl`, `ExtractLargeValueIfNeeded`, `GarbageCollectBlobIfNeeded`, `ExtractLargeColumnValuesIfNeeded`, `FetchBlobsNeedingGC`, `RelocateBlobValues`, `SerializeEntityAfterGC`, and `GarbageCollectEntityBlobsIfNeeded`. Static helpers compute blob GC cutoff file numbers and construct blob fetch/prefetch resources.

## Control flow

The iterator runs as a loop over an already sorted `InternalIterator`. Each candidate input record is parsed into `ikey_`, with `key_` and `value_` initially pointing at the input. Range-deletion sentinel keys are surfaced immediately. Point keys enter user-key tracking: for a new user key or a new user-defined timestamp bucket, `current_key_` copies the internal key, timestamp state is refreshed, `current_user_key_sequence_` and `current_user_key_snapshot_` reset, and the first committed version may pass through the compaction filter.

The snapshot stripe logic compares the candidate sequence to the configured snapshots, plus optional `SnapshotChecker`, to find the earliest snapshot that can see the candidate. If a newer version for the same user key is visible to the same or a later snapshot stripe, rule A drops the older record as hidden. When a `SnapshotChecker` says a key is not committed at the compaction job snapshot, the iterator keeps it without normal compaction so transaction engines do not lose unresolved writes.

SingleDelete is handled with lookahead because correctness depends on the following point key. The code skips range tombstone sentinels with the same user key, then checks whether the next real key is a matching value-like record in the same snapshot stripe. Depending on timestamp GC eligibility, prior output in the stripe, write-conflict snapshot requirements, bottommost state, and lower-level existence, it can drop both records, keep the SingleDelete, keep the SingleDelete and clear the matching value's payload for a later output, report contract violations, or drop fall-through SingleDeletes that cannot affect future reads.

Deletion markers can be dropped when the compaction proves no lower/higher output-level data can make them visible and they are visible to the earliest snapshot. Bottommost deletions get a special path that skips same-stripe older versions and keeps the deletion only if another version in an older snapshot still needs it. Range tombstones are queried through `CompactionRangeDelAggregator::ShouldDelete` for ordinary point keys and timed puts.

Merge operands are delegated to `MergeHelper::MergeUntil`. The compaction iterator pins input blocks while the merge helper consumes operands, then emits `MergeOutputIterator` records before returning to the main input stream. A `MergeInProgress` status is treated specially so partial merge output can be written before a remaining base record.

Timed put (`kTypeValuePreferredSeqno`) entries can swap in their packed preferred sequence number only when they are visible to the earliest snapshot and no lower-level key can reappear. The code also checks whether swapping would make a range tombstone cover the key; if so it leaves the timed put unchanged.

After `NextFromInput` marks a record valid, `PrepareOutput` performs value representation changes and bottommost sequence zeroing. This separation keeps visibility/drop decisions distinct from output serialization.

## State and persistence behavior

`current_key_` owns the current output key buffer when the input key needs rewriting. `key_` and `value_` are slices into either input data or internal buffers such as `current_key_`, `blob_index_`, `blob_value_`, `compaction_filter_value_`, or `rewritten_entity_`. `at_next_` records lookahead consumption so `Next` does not accidentally skip the already positioned input. `has_current_user_key_`, `current_user_key_`, `current_user_key_sequence_`, and `current_user_key_snapshot_` define the active user-key stripe. `has_outputted_key_`, `clear_and_output_next_key_`, `last_key_seq_zeroed_`, and `current_key_committed_` refine SingleDelete, snapshot, and transaction behavior.

`validity_info_` compactly stores valid/invalid plus a debug context enum, which helps identify why a record was surfaced. `status_` is sticky for hard failures such as corrupt internal keys, missing merge operator, unsupported blob filtering context, blob read errors, compaction filter IO errors, serialization failures, shutdown, or manual compaction pause.

Persistent effects are indirect: the iterator itself does not write table files, but its output controls what table builders persist. It can remove obsolete records, rewrite internal key types, zero sequence numbers, rewrite user timestamps to zero for timestamp GC, emit blob index values, inline relocated blob values, or serialize V2 wide-column entities with blob references. Blob file persistence is delegated to `BlobFileBuilder::Add` and `Finish` outside this file.

Input-entry counting is mediated by `SequenceIterWrapper`. If exact counting is required, seeks are emulated by repeated `Next` calls; otherwise skip-until/filter seeks invalidate exact count availability.

## Dependencies and integration points

The implementation integrates with `InternalIterator`, `InternalKeyComparator`, `ParsedInternalKey`, `MergeHelper`, `CompactionRangeDelAggregator`, `SnapshotChecker`, `Compaction`, `Version`, `VersionStorageInfo`, `BlobFetcher`, `BlobFileBuilder`, `BlobIndex`, `PrefetchBufferCollection`, `WideColumnSerialization`, `WideColumnsHelper`, `CompactionFilter`, `Env`, `SystemClock`, RocksDB logging, and sync points.

The `CompactionProxy` abstraction, declared in the header, lets tests provide only the subset of compaction behavior needed by this iterator. Real production compactions use `RealCompaction` to forward bottommost, level, lower-level existence, blob GC, mmap, readahead, and ingest-behind decisions.

The file supports both integrated BlobDB behavior and stacked BlobDB's older compaction-filter-based GC behavior. It also supports non-compaction table-file creation through `input_version` and `SetBlobFetcher`, which is important for flush or recovery paths that can encounter direct-write wide entities containing blob references.

## Risks and edge cases

Snapshot and transaction semantics are the main risk. Dropping a record too aggressively can make old snapshots incorrect or break write-prepared/write-unprepared conflict checking. The `SnapshotChecker` and `released_snapshots_` behavior is subtle because a released snapshot must not become the earliest visible snapshot for older values.

SingleDelete handling is high risk because it uses lookahead and makes decisions from a combination of matching key type, snapshot stripe, write-conflict snapshot, timestamp GC eligibility, lower-level existence, and configured contract enforcement. The `clear_and_output_next_key_` optimization intentionally emits an empty value after a kept SingleDelete; consumers must preserve that behavior.

Blob and wide-column paths are high risk for lifetime and serialization issues. `value_` can point into several temporary buffers, lazy blob resolution caches fetched values, and `entity_deserialized_` is reused to avoid double deserialization. The code explicitly resets this state at loop boundaries and after filter rewrites to prevent stale entity data from leaking into another record.

Filter APIs can seek the input and can rewrite key types. `RemoveAndSkipUntil` must reject backwards skip targets, and `kChangeBlobIndex`/`kIOError` are restricted to stacked BlobDB internal filters. Lazy FilterV4 resolution intentionally fails compaction if blob fetching failed during inspection.

Timestamp GC only operates when comparator timestamp size and `full_history_ts_low_` are configured consistently. Incorrect timestamp comparison can collapse or preserve too much history, especially with range tombstones and bottommost sequence zeroing.

## Test signals

`compaction_iterator_test.cc` exercises the main state machine: empty outputs, corrupt keys, SingleDelete with values, range deletion, filter skip-until seeks, shutdown during filter and merge, merge output, bottommost deletion removal, sequence zeroing, timed put preferred sequence swaps, snapshot checker behavior, ingest-behind behavior, user timestamp GC, wide-column blob extraction, wide-column blob reference preservation, lazy resolver null-fetcher behavior, and deserialization cache reset after filtered entities.

Additional integration signals are noted in comments for real blob GC with `Version`, especially wide-column entity blob GC coverage in broader DB tests. The tests emphasize expected output key/value sequences and iterator call logs, which is appropriate because much of this file's correctness is observable as exact output ordering and exact input advancement behavior.
