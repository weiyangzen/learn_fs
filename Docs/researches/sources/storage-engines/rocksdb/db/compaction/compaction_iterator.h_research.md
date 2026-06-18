# sources/storage-engines/rocksdb/db/compaction/compaction_iterator.h

## Purpose

`compaction_iterator.h` declares the public and private contract for RocksDB's compaction output iterator. It defines the narrow API used by compaction/table-building code, the small `CompactionProxy` abstraction that decouples iterator logic from full `Compaction`, the `SequenceIterWrapper` used to count scanned input entries, and the `CompactionBlobResolver` used by wide-column compaction filters.

The header is a map of the iterator's responsibilities. It shows that compaction iteration is not simply deduplication; it coordinates snapshots, transaction commit visibility, range deletions, merge helpers, compaction filters, user-defined timestamps, blob extraction, blob relocation, wide-column entity serialization, input scan accounting, and shutdown/manual pause handling.

## Important APIs, types, and fields

`CompactionBlobResolver` derives from `WideColumnBlobResolver`. It exposes `Init`, `Reset`, `ResolveColumn`, `IsBlobColumn`, `NumColumns`, and `resolve_status`. It stores the current user key, column vector, blob-column side list, blob fetcher, prefetch buffers, iteration stats, a small resolved-value cache, and optional sticky error state.

`SequenceIterWrapper` derives from `InternalIterator` and wraps another internal iterator without owning it. It increments `num_itered_` on `Next` except for delete-range sentinel keys. Its `Seek` either delegates directly and marks counts unreliable, or simulates seek with repeated `Next` when exact counting is required. `HasNumItered` and `NumItered` expose count validity and value.

`CompactionIterator::CompactionProxy` is the reduced compaction interface needed by the iterator: level, bottommost status, number of levels, lower-level key existence checks, largest user key, ingest-behind, mmap reads, blob GC options, blob readahead, input version, blob-file reference checks, access to the real compaction, and per-key placement support. `RealCompaction` implements this by forwarding to `Compaction`.

The public `CompactionIterator` API consists of two constructors, destructor, `ResetRecordCounts`, `SetBlobFetcher`, `SeekToFirst`, `Next`, accessors for `key`, `value`, `status`, `ikey`, `Valid`, `user_key`, `iter_stats`, input-entry scan state, `InputStatus`, and `IsDeleteRangeSentinelKey`.

Important private methods are `NextFromInput`, `PrepareOutput`, blob extraction/GC helpers, `InvokeFilterIfNeeded`, `findEarliestVisibleSnapshot`, `KeyCommitted`, snapshot helper predicates, timestamp update, and blob fetcher/prefetch factory helpers.

`ValidContext` records why a candidate output is valid, including merge paths, parse error, uncommitted key, SingleDelete cases, timestamp-history keep, deletion keep, new user key, range deletion, and preferred-sequence swap. `ValidityInfo` stores valid bit plus context in a byte.

## Control flow represented by the declarations

Callers create `CompactionIterator` with an already positioned or positionable input iterator, comparator, merge helper, snapshot vector, range tombstone aggregator, and optional compaction/filter/blob dependencies. `SeekToFirst` begins producing output. Each `Next` either drains pending merge output or advances the wrapped input, then calls into the private input-processing and output-preparation stages.

The header's private method split indicates the major phases. `NextFromInput` decides which input record becomes a logical output and which records are skipped. `PrepareOutput` performs final rewrites on that logical output. Filter invocation is separated from both so the iterator can apply filters only to the first committed version of a user key or merge-helper-managed operands.

The blob helper API shows a two-family design: ordinary value/blob-index records use `ExtractLargeValueIfNeeded` and `GarbageCollectBlobIfNeeded`; wide-column entities use `ExtractLargeColumnValuesIfNeeded` and `GarbageCollectEntityBlobsIfNeeded`, with helper methods for fetching, relocating, and serializing only the relevant blob-backed columns.

## State and persistence behavior

The iterator holds several classes of state. Input and dependencies include `input_`, `cmp_`, `merge_helper_`, `snapshots_`, `snapshot_checker_`, `range_del_agg_`, `blob_file_builder_`, `compaction_`, `compaction_filter_`, `shutting_down_`, `manual_compaction_canceled_`, and timestamp-history settings.

Visibility state includes `earliest_write_conflict_snapshot_`, `job_snapshot_`, `earliest_snapshot_`, `visible_at_tip_`, `released_snapshots_`, `current_key_committed_`, `current_user_key_sequence_`, and `current_user_key_snapshot_`. These fields preserve transaction and snapshot correctness across multiple versions of the same user key.

Output lifetime state includes `key_`, `value_`, `ikey_`, `current_key_`, `current_user_key_`, `curr_ts_`, `status_`, `validity_info_`, `has_current_user_key_`, `at_next_`, `has_outputted_key_`, `clear_and_output_next_key_`, and `last_key_seq_zeroed_`. These fields let the iterator point to input memory when safe and use owned buffers when rewriting internal keys or values.

Blob and wide-column state includes `blob_garbage_collection_cutoff_file_number_`, `blob_fetcher_`, `prefetch_buffers_`, `blob_index_`, `blob_value_`, `compaction_filter_value_`, `rewritten_entity_`, `entity_columns_`, `entity_blob_columns_`, `entity_wide_columns_`, `filter_existing_columns_`, `blob_resolver_`, and `entity_deserialized_`. These fields reduce allocations and preserve slice lifetimes during filter, extraction, and GC work.

The iterator itself does not persist files, but the state declared here determines what downstream table builders and blob builders persist. It can surface rewritten keys and values, expose blob index values created by `BlobFileBuilder`, and update `CompactionIterationStats` for records dropped, bytes read, blobs relocated, and filter time.

## Dependencies and integration points

This header depends on RocksDB internals including blob index/build/fetch abstractions, compaction metadata, compaction iteration stats, merge helper, pinned iterator manager, range deletion aggregator, snapshot checker, column-family options, compaction filter API, and `Slice`. It forward-declares blob/cache/version/prefetch types where possible to keep compile dependencies lower.

The public constructor signatures are integration-heavy. They are used by real compaction code and also by flush/recovery-style paths that may not have a `Compaction` but still need blob resolution through `input_version` or `SetBlobFetcher`. The custom `CompactionProxy` constructor is explicitly for tests and allows targeted validation without constructing full RocksDB version/compaction state.

`CompactionIterator` also integrates with merge operators through `MergeHelper`, with `CompactionFilter` versions through filter support flags and resolver callbacks, with manual compaction cancellation through an atomic flag, and with input scan accounting through `SequenceIterWrapper`.

## Risks and edge cases

The constructor surface is broad, and many arguments are raw pointers whose lifetime must outlive the iterator: input iterator, comparator, merge helper, snapshots vector, environment, range deletion aggregator, blob file builder, compaction filter, shutdown flag, timestamp lower bound, and optional input version. Mismanaged lifetimes would cause slice or pointer invalidation.

`SequenceIterWrapper` count accuracy depends on whether `Seek` was used and whether exact counting was requested. Consumers must call `HasNumInputEntryScanned` before trusting `NumInputEntryScanned` unless `must_count_input_entries` was true.

Many state fields are reused across records for performance. The header makes clear that `entity_deserialized_`, wide-column buffers, blob resolver cache, `compaction_filter_value_`, and `rewritten_entity_` require careful reset discipline in the implementation.

Snapshot correctness depends on sorted `snapshots_`, valid `earliest_snapshot_`, `preserve_seqno_min`, and compatible `SnapshotChecker`. Debug assertions check some invariants, but production correctness still depends on callers providing coherent compaction context.

Blob GC factory helpers depend on `Version` and `VersionStorageInfo` when compaction enables blob GC. Test proxies that report blob GC without a real version would violate implementation assertions.

## Test signals

The companion test file constructs `CompactionIterator` through the proxy constructor, validating that the reduced `CompactionProxy` interface is sufficient for bottommost, ingest-behind, lower-level existence, and blob-reference scenarios. Tests also exercise `SequenceIterWrapper` indirectly by checking logged input `Next` and `Seek` calls for compaction filter skip-until behavior.

`CompactionBlobResolver` has explicit tests for null fetcher behavior, blob-column detection, non-blob column resolution, and multi-column resolution failure. Wide-column tests validate the `entity_deserialized_` optimization and reset behavior implied by the header's reusable state fields.
