# sources/storage-engines/rocksdb/db/external_sst_file_ingestion_job.cc

## Purpose
`external_sst_file_ingestion_job.cc` implements the internal job that turns caller-supplied external SST files into RocksDB version edits. It reads and validates table metadata, copies or links files into DB-owned paths, verifies or generates checksums, decides whether input files overlap, batches overlapping input files, assigns target levels and global sequence numbers, updates on-disk global seqno fields when requested, constructs `FileMetaData`, records equivalent compactions for range conflict checks, updates stats/events, and cleans up files on success or failure.

This file is the transactional core under `DB::IngestExternalFile(s)`. The caller is responsible for higher-level write-thread coordination and manifest application; the job prepares durable files and a `VersionEdit` that can be applied to make ingestion visible.

## Important APIs, Types, And Functions
`ExternalSstFileIngestionJob::Prepare` is the pre-manifest phase. It calls `GetIngestedFileInfo` for each path, validates column-family IDs and non-empty/correct key ranges, handles `atomic_replace_range`, rejects unsupported overlapping input modes, copies or links files, fsyncs files/directories, performs checksum generation/verification, and calls `DivideInputFilesIntoBatches`.

`Run` is the manifest-edit construction phase. It checks memtable state when the caller flushed before run, enforces no remaining flush need in debug builds, determines whether snapshots force global seqnos, deletes existing files for `atomic_replace_range`, assigns levels/seqnos per batch, and creates equivalent compactions.

Other key functions are `NeedsFlush`, `MergeForSameColumnFamily`, `ComputeFilesOverlap`, `AssignLevelsForOneBatch`, `AssignLevelAndSeqnoForIngestedFile`, `CheckLevelForIngestedBehindFile`, `AssignGlobalSeqnoForIngestedFile`, `GenerateChecksumForIngestedFile`, `GetIngestedFileInfo`, `SanityCheckTableProperties`, `ResetTableReader`, `GetSeqnoBoundaryForFile`, `IngestedFileFitInLevel`, `CreateEquivalentFileIngestingCompactions`, `RegisterRange`, `UnregisterRange`, `UpdateStats`, `Cleanup`, and `DeleteInternalFiles`.

## Control Flow
Preparation starts by scanning every external path. For each file, the job creates a DB file descriptor, opens a `TableReader`, validates external SST version/global seqno properties, validates comparator and user-defined timestamp compatibility, optionally computes existing DB-generated seqno boundaries, verifies checksums, obtains smallest/largest point keys, expands bounds with range tombstones, derives user-key overlap bounds, and extracts a unique ID.

After input metadata is collected, the job detects input-file overlap by sorting range pointers and checking adjacent ranges with `ExternalFileRangeChecker`. Overlap affects batching and sequence-number assignment. Overlapping files cannot be ingested behind, require global seqnos unless DB-generated files are allowed, and are disallowed for user-defined timestamp column families.

The copy/link phase places every file at its final DB table filename. `move_files` or `link_files` first try `LinkFile`; unsupported links can fall back to copy if configured. Linked files are explicitly synced because applications may not have synced the source. Copied files use `CopyFile`, which also syncs and may change the destination temperature based on write or last-level temperature options. Data directories are fsynced after files are added.

Checksum handling has two phases. During `Prepare`, if a DB checksum factory exists, the job either trusts complete caller-provided checksums when verification is disabled or generates checksums and compares them to caller input when verification is enabled. If `write_global_seqno` will mutate the file later, final manifest checksum generation is deferred. During `Run`, after global seqno assignment, `GenerateChecksumForIngestedFile` recomputes checksum metadata for the manifest when needed.

`Run` uses current `SuperVersion` storage info. For atomic replace, it emits `DeleteFile` edits for fully covered existing files and rejects pending compaction overlap or partial overlap. For each batch, `AssignLevelAndSeqnoForIngestedFile` walks levels from top toward the allowed boundary, checks pending compactions and existing file overlap, chooses the lowest fitting level, and assigns `last_seqno + 1` when snapshots, input overlap, L0/FIFO placement, or DB overlap require ordering. Each ingested file becomes a `FileMetaData` added to the `VersionEdit`.

## State And Persistence Behavior
The job owns transient vectors of `IngestedFileInfo`, `FileBatchInfo`, equivalent `Compaction` objects, and temporary `FileMetaData` allocations. It also accumulates persistent intent in `edit_`: delete edits for atomic replacement and add edits for ingested files.

On disk, `Prepare` creates or links internal SST files in DB data paths and fsyncs files/directories. `AssignGlobalSeqnoForIngestedFile` may open the internal file as `FSRandomRWFile`, write the encoded sequence number at the table property offset, and sync the modified file. `Cleanup` deletes internal files on failure; on success with `move_files`, it deletes original external links. Successful ingestion persists metadata only when the caller later applies `edit_` to the manifest.

File metadata carries level, file number/path ID/size, internal key bounds, smallest/largest sequence numbers, temperature, epoch number, checksum and checksum function name, unique ID, tail size, timestamp persistence flag, min/max timestamp properties, file-open metadata when fast SST open is enabled, and a marked-for-compaction bit for standalone range deletion files.

## Dependencies And Integration Points
The implementation depends on `VersionSet`, `ColumnFamilyData`, `SuperVersion`, `VersionStorageInfo`, `TableReader`, table factories, `SstFileWriter` external properties, `FileSystem`, `Directories`, `CopyFile`, checksum generators, `IOTracer`, `EventLogger`, internal stats, compaction picker, `RangeOverlapWithCompaction`, `OverlapWithLevelIterator`, `SnapshotList`, user-defined timestamp utilities, unique-ID helpers, sync points, and RocksDB logging/status APIs.

It integrates with write-thread orchestration through mutex/write-thread preconditions on `Run`, `RegisterRange`, `UnregisterRange`, and `UpdateStats`. Equivalent compactions are registered with the compaction picker so ingestion ranges conflict with concurrent compactions. `MergeForSameColumnFamily` supports combining prepared handles for a single column family while preserving user-specified file order and higher-seqno-wins semantics.

## Risks And Edge Cases
Range comparison is built on internal keys and comments warn the `sstableKeyCompare` approach with user comparators is fragile. Range tombstones require special bound updates, and user-defined timestamps require comparing user keys without timestamp bytes by constructing max/min timestamp versions.

Correct sequence-number behavior is central. Files with existing nonzero sequence numbers are rejected unless `allow_db_generated_files` is enabled. DB-generated files may not overlap existing DB data because the job will not rewrite their seqnos. Snapshot consistency, overlapping input files, L0/FIFO placement, pending compaction overlap, and existing-level overlap all force assigned seqnos. If `allow_global_seqno` is false, those cases fail.

Atomic replacement is conservative: full-CF replacement fails while any compaction is in progress; ranged replacement rejects pending compaction overlap, partial file overlap, unsupported one-sided ranges upstream, and files outside the replace range. The code comments note that synthesizing tombstone files for partial overlap is a future possibility.

Filesystem behavior is another risk surface. Linking can fail or be unsupported; syncing linked files can fail except `NotSupported` is ignored for some filesystems; random-write support controls whether global seqno can be physically written; checksum generation reads whole files and TODOs mention rate limiting and IO activity plumbing. Cleanup logs deletion failures but cannot guarantee all artifacts are removed if the filesystem fails.

## Test Signals
This file is heavily exercised by `external_sst_file_basic_test.cc` and related ingestion tests. Useful signals are successful ingestion plus correct DB reads, expected `InvalidArgument`, `TryAgain`, `NotSupported`, or `Corruption` failures, manifest file metadata matching checksum/temperature/unique ID/seqno expectations, no leaked internal files after failed ingestion, source-file deletion after successful move ingestion, level counts after overlapping batches, internal stats/event logger updates, and sync point paths around file sync, directory sync, random write, seqno sync, overlap detection, and seqno-boundary file scans.
