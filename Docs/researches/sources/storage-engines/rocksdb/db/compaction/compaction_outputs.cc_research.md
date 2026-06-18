# sources/storage-engines/rocksdb/db/compaction/compaction_outputs.cc

## Purpose
This file implements `CompactionOutputs`, the per-subcompaction output manager used by `CompactionJob`. It owns the active table builder/file writer lifecycle, records output file metadata and stats, decides when an output file should be cut, writes point keys and range tombstones, accounts blob garbage, captures table properties, and prepares output boundary state needed by later version installation.

## Important APIs, Types, and Functions
The main methods are `NewBuilder`, `Finish`, `WriterSyncClose`, `UpdateFilesToCutForTTLStates`, `UpdateGrandparentBoundaryInfo`, `GetCurrentKeyGrandparentOverlappedBytes`, `ShouldStopBefore`, `AddToOutput`, `AddRangeDels`, `FillFilesToCutForTtl`, and the constructor. The anonymous helper `SetMaxSeqAndTs` builds internal range-deletion boundary keys with maximum timestamp bytes when user-defined timestamps are enabled.

`Finish` finalizes the table builder, attaches seqno-to-time table properties, extracts timestamp table properties into `FileMetaData`, records file size, tail size, compaction-needed flag, write/pre-compression bytes, output-file count, and worker CPU micros. `WriterSyncClose` prepares compaction IO options, syncs and closes the writer, then stores checksum metadata in the output file metadata.

## Control Flow
`AddToOutput` is called for each `CompactionIterator` output key. It first skips range deletion sentinel handling for bottommost-level cases where tombstones may be dropped. It calls `ShouldStopBefore`; if a current builder exists and a cut is needed, it invokes the caller-provided close function, resets grandparent overlap state, and records a range tombstone lower bound when the next output starts with a range tombstone sentinel. It then opens a new output through the caller-provided open function if needed. Point keys are validated by `OutputValidator`, added to the table builder, counted in stats, optionally passed through `BlobGarbageMeter`, tracked for preferred sequence numbers, and used to update `FileMetaData` boundaries.

`ShouldStopBefore` always updates grandparent and TTL-cut state for non-L0 outputs before checking the active builder. It cuts on TTL isolation, required partitioner boundaries, target file size, round-robin output split key, excessive current-output plus grandparent overlap against `max_compaction_bytes`, large skippable grandparent gaps, and dynamic pre-cuts at grandparent boundaries. It deliberately avoids splitting L0 outputs and avoids cutting before the first key because no builder exists yet.

`AddRangeDels` computes lower and upper internal-key guards for the current output file, including subcompaction start/end boundaries and next-table minimum key. It iterates a bounded `CompactionRangeDelAggregator`, filters tombstones by per-key-placement sequence range, clamps tombstone start/end keys to the output range, drops obsolete tombstones at bottommost or when no lower-level key range exists, adds surviving tombstones to the builder, updates file range boundaries, and estimates compensated range deletion size for non-bottommost output.

## State and Persistence Behavior
Persistent state produced here includes SST bytes, table properties, file checksum fields, file size/tail size, smallest/largest keys, sequence range, timestamp-persisted metadata, oldest ancestor time table properties, and compensated range deletion size. In-memory output state includes the builder, file writer, list of outputs, blob file additions, blob garbage meter, output file paths for abort cleanup, stats, partitioner state, round-robin split state, TTL-cut file cursor, grandparent overlap cursor, and level pointers for range tombstone existence checks.

## Dependencies and Integration Points
The implementation depends on `NewTableBuilder`, `WritableFileWriter`, `TableBuilderOptions`, `CompactionIterator`, `CompactionRangeDelAggregator`, `Compaction`, `VersionSet::ApproximateSize`, `OutputValidator`, blob garbage metering, user comparators with optional timestamps, internal key encoding/parsing, sync points, and compaction/job callbacks for opening and closing files. It is tightly coupled to `CompactionJob` because open/close functions own file-number allocation and manifest-facing installation while `CompactionOutputs` owns builder-local state.

## Risks and Edge Cases
The highest-risk code is boundary math. Incorrect lower/upper guards in `AddRangeDels` can lose tombstone coverage or create overlapping output files. Same-user-key grandparent boundaries must not split versions in a way that breaks reads. Blob-aware per-key placement uses sequence ranges, so tombstone filtering must match output placement. TTL cuts depend on file oldest-ancestor time and can produce extra small files if thresholds are wrong. `WriterSyncClose` only stores checksum metadata when prior status and sync/close status are OK, so error precedence matters. Range tombstone compensated size can double count tombstones spanning outputs, which is noted in comments.

## Test Signals
`compaction_job_test.cc` directly exercises output cutting for max compaction bytes, skippable grandparents, grandparent-boundary alignment, and same-key boundaries. Timestamp tests validate range/key GC interaction. Blob metadata tests cover oldest blob file tracking, and IO-priority tests validate file writer/read paths. Additional coverage likely comes from broader RocksDB compaction, range deletion, blob DB, and partitioner tests.
