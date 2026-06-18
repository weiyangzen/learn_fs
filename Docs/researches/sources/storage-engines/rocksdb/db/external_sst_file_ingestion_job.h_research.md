# sources/storage-engines/rocksdb/db/external_sst_file_ingestion_job.h

## Purpose
`external_sst_file_ingestion_job.h` declares the data structures and job API used to ingest external SST files into a RocksDB column family. It defines range metadata, file metadata collected from external tables, batching metadata for overlapping inputs, and the `ExternalSstFileIngestionJob` class that prepares files, checks flush needs, creates version edits, registers range conflicts, updates stats, and cleans up.

The header captures the contract between DB ingestion orchestration and the implementation file. It makes clear which methods require the DB mutex, which operations are thread-safe, and which state is prepared before the final manifest edit is applied.

## Important APIs, Types, And Functions
`KeyRangeInfo` stores smallest and largest `InternalKey` bounds. Its `unset()` helper treats unset internal keys as invalid or unbounded sentinel values.

`ExternalFileRangeChecker` wraps a user comparator and supplies ordering, overlap, containment, and range-extension helpers. `operator()` sorts `KeyRangeInfo` pointers by smallest internal key. `Overlaps` supports a fast path when sorted ranges are known ordered. `Contains` validates range containment. `MaybeUpdateRange` expands a `KeyRangeInfo` with new start/end internal keys.

`IngestedFileInfo` extends `KeyRangeInfo` with external path, timestamp-aware user-key overlap bounds, original and assigned sequence numbers, global seqno offset, file size, entry and range deletion counts, column-family ID, table properties, external file version, destination `FileDescriptor`, internal path, picked level, copy/link decision, checksum metadata, temperature, unique ID, user-defined timestamp persistence flag, and seqno boundaries for DB-generated files.

`FileBatchInfo` extends `KeyRangeInfo` and groups `IngestedFileInfo*` values. Its `track_batch_range` flag controls whether `AddFile` maintains the batch's aggregate range. Non-overlapping inputs can skip range tracking in a single default batch; overlapping inputs use tracked batches to preserve order while avoiding overlap within a batch.

`ExternalSstFileIngestionJob` exposes `Prepare`, `NeedsFlush`, `SetFlushedBeforeRun`, `Run`, `RegisterRange`, `UnregisterRange`, `UpdateStats`, `Cleanup`, `edit`, `files_to_ingest`, `MaxAssignedSequenceNumber`, and `MergeForSameColumnFamily`.

## Control Flow
The public lifecycle is:

1. Construct the job with version-set, column-family, immutable/mutable DB options, env options, snapshot list, ingestion options, directories, event logger, and IO tracer.
2. Call `Prepare` with external paths, optional checksum vectors, optional atomic replace range, temperature hint, next file number, and `SuperVersion`. This fills `files_to_ingest_`, copies or links files into DB storage, validates input metadata, and forms file batches.
3. Call `NeedsFlush` as needed to decide whether memtables overlap the ingested ranges or atomic replace range. If a flush is performed, call `SetFlushedBeforeRun`.
4. Under the DB writer/mutex protocol, call `Run` to assign levels/seqnos and populate `edit_`.
5. Register equivalent compaction ranges before manifest application when needed, then unregister on destruction or explicit cleanup.
6. Call `UpdateStats` after success and `Cleanup` with the final status to delete temporary internal files on failure or remove original moved files on success.

Private helpers in the class declaration show the major implementation phases: table-reader reset, table-property sanity checks, ingested-file metadata extraction, overlap batching, level and seqno assignment, ingest-behind validation, global seqno writing, checksum generation, level fit checks, syncing, DB-generated seqno boundary scanning, equivalent compaction creation, and failed-file deletion.

## State And Persistence Behavior
Most fields are borrowed pointers or references to DB-owned state: `VersionSet`, `ColumnFamilyData`, comparators, options, snapshots, directories, and event logger. Job-owned mutable state includes `files_to_ingest_`, `file_batches_to_ingest_`, `atomic_replace_range_`, `edit_`, `job_start_time_`, `max_assigned_seqno_`, `files_overlap_`, `need_generate_file_checksum_`, `flushed_before_run_`, and vectors holding equivalent compaction objects.

The header documents that `MaxAssignedSequenceNumber` has two interpretations. With normal external files, assigned global seqnos follow `versions_->LastSequence()` when global seqno assignment is needed. With `allow_db_generated_files=true`, files already carry sequence numbers, so the max is the largest seqno observed in the ingested files.

Persistent effects are not applied directly by the header API, but the job prepares them through `edit_` and DB-owned internal file paths. `Cleanup` semantics are part of the public contract: failed jobs delete internal files; successful move ingestion removes original paths.

## Dependencies And Integration Points
The header depends on RocksDB internal DB metadata (`column_family.h`, `internal_stats.h`, `snapshot_impl.h`, `version_edit.h`), filesystem tracing and file-system abstractions, event logging, DB options, public `rocksdb/db.h` and `rocksdb/sst_file_writer.h`, and `autovector`.

`ExternalSstFileIngestionJob` is integrated into DB ingestion code that owns write serialization, super-version lifetime, manifest application, sequence-number advancement, and column-family lifetime. It also integrates with compaction conflict tracking by creating `Compaction` objects equivalent to the ingestion's output ranges and registering them with the column family's compaction picker.

## Risks And Edge Cases
The range checker works on internal keys and asserts that ranges are set and legal. Bad unset handling can silently return false in release builds after an assertion path, so callers must validate table key bounds before overlap checks.

`IngestedFileInfo` carries two sets of range concepts: internal key bounds for manifest metadata and `start_ukey`/`limit_ukey` for overlap checks without user-defined timestamp bytes. Mixing those fields would break UDT ingestion and overlap detection. The default `copy_file=true` is intentional to avoid undefined behavior before options decide copy versus link.

Batching order matters for overlapping inputs: later files are meant to win by receiving higher sequence numbers. `MergeForSameColumnFamily` also preserves append order for this reason. Atomic replace range, ingest-behind, bottommost-level requirements, and DB-generated file ingestion all restrict which helper paths are legal.

## Test Signals
The header's contract is indirectly validated by the external SST ingestion tests. Relevant signals include correct `files_to_ingest()` metadata after prepare, `NeedsFlush` decisions for point and range-tombstone overlaps, `edit()` containing expected add/delete file edits, `MaxAssignedSequenceNumber()` matching sequence advancement, range registration preventing compaction conflicts, successful cleanup behavior, and compile-time enforcement of method signatures used by DB ingestion orchestration.
