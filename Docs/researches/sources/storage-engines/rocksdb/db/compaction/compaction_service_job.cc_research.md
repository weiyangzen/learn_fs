<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_service_job.cc -->
# sources/storage-engines/rocksdb/db/compaction/compaction_service_job.cc

## Purpose
This file implements RocksDB's remote compaction service bridge. On the primary DB side, it serializes a compaction request, schedules and waits on a `CompactionService`, imports remote SST outputs, reconstructs file metadata/stats, and notifies the service of installation status. On the worker side, `CompactionServiceCompactionJob` runs `DB::OpenAndCompact` work in an isolated output directory and serializes a `CompactionServiceResult`.

## Important APIs, Types, and Functions
The primary entry point is `CompactionJob::ProcessKeyValueCompactionWithCompactionService(SubcompactionState*)`. Worker-side methods include `CompactionServiceCompactionJob::Prepare`, `Run`, `CleanupCompaction`, `GetTableFileName`, and `RecordCompactionIOStats`. Serialization APIs are `CompactionServiceInput::Read/Write`, `CompactionServiceResult::Read/Write`, and debug-only `TEST_Equals` helpers.

The file defines option-style descriptors for `ColumnFamilyDescriptor`, `CompactionServiceInput`, `CompactionServiceOutputFile`, `CompactionJobStats`, `InternalStats::CompactionStats`, `InternalStats::CompactionStatsFull`, and `CompactionServiceResult`. `StatusSerializationAdapter` exposes private `Status` fields so status can be serialized through the same option framework. The only binary format version currently supported is `kOptionsString`.

## Control Flow
On the primary path, `ProcessKeyValueCompactionWithCompactionService` builds `CompactionServiceInput` from compaction output level, DB identity, input table file names, column-family name, snapshot sequence numbers, subcompaction bounds, and the pinned options file number. It serializes this request and calls `CompactionService::Schedule` with `CompactionServiceJobInfo`. Schedule responses can continue, abort, fail, or request local fallback.

After successful scheduling, the primary waits for a result. `kUseLocal` returns local fallback. `kAborted` and `kFailure` set the subcompaction status from either the returned `CompactionServiceResult` or an incomplete status. If wait succeeds but result deserialization fails, no remote output has been imported, so the primary calls `OnInstallation(kUseLocal)` and asks the caller to rerun locally. With a valid result, each remote output file is renamed from the service output path into the DB table path under a fresh primary-side file number. The code reconstructs `FileMetaData`, decodes smallest/largest internal keys, fills checksum, unique ID, temperature, table properties and tail size, adds outputs to normal or proximal `CompactionOutputs`, updates internal/job stats, records remote read/write ticks, and calls `OnInstallation(kSuccess)`.

On the worker path, `CompactionServiceCompactionJob::Prepare` converts request begin/end strings into optional slices and calls base `CompactionJob::Prepare`. `Run` logs the compaction, initializes input table properties, processes the single subcompaction locally, fsyncs the output directory, aggregates output and job stats, marks stats as remote/manual/full as appropriate, records I/O stats, and fills `CompactionServiceResult` with output file metadata and table properties.

## State and Persistence Behavior
Primary-side persistence is the atomic movement of remote-created table files into the primary DB's table namespace using new file numbers from `VersionSet`. Only after file rename and metadata reconstruction do outputs become candidates for installation into the new version. Failure during rename or file-size lookup marks the subcompaction failed and notifies `OnInstallation(kFailure)`. A deserialization failure before import is explicitly safe for local fallback because remote outputs remain isolated in the service-managed output directory.

Worker-side persistence is isolated to the output directory passed to `OpenAndCompact`. The result records every output file's name, size, sequence range, internal key bounds, ancestor/creation times, epoch, checksum information, paranoid hash, marked-for-compaction bit, unique ID, table properties, proximal-output flag, and file temperature. Serialization prepends a 32-bit format version and then uses option string serialization with unknown-option tolerance on read for forward compatibility.

## Dependencies and Integration Points
The file depends on `CompactionJob`, `CompactionState`, `SubcompactionState`, `CompactionOutputs`, `VersionSet`, table/file naming, `FileSystem` rename and size APIs, table properties, `OptionTypeInfo`, `ConfigOptions`, `Status`, statistics tickers, histograms, log buffers, thread status, and I/O stats. It integrates with public `CompactionService`, `CompactionServiceJobInfo`, `CompactionServiceOptionsOverride`, `OpenAndCompactOptions`, and DB secondary/open-and-compact code. It also coordinates with output verification, paranoid hash validation, per-key placement/proximal outputs, and local fallback behavior in `compaction_job.cc`.

## Risks and Edge Cases
Remote compaction has several sharp edges: malformed results must not install partial output, remote failures must preserve meaningful status, file-number collisions are avoided by allocating fresh primary numbers, and missing `file_size` from older workers is backfilled from the filesystem. The result serialization is broad and must stay compatible with `CompactionJobStats`, table properties, status representation, and `CompactionReason` count arrays. Whole-file input filtering can make iterator-count verification inaccurate, so the worker explicitly clears `has_accurate_num_input_records` when filtered input levels are present.

The TODO about abort/resume support notes that the service API cannot fully signal remote abort/resume yet. There is also a compatibility risk around arrays sized to `CompactionReason::kNumOfReasons - 1`, called out in a comment as a release workaround.

## Test Signals
`compaction_service_test.cc` is the primary behavioral suite for this file. `compaction_job_test.cc` has serialization round-trip coverage for `CompactionServiceInput` and `CompactionServiceResult`. Strong signals include successful local fallback on invalid result, failed installation on rename/verification errors, correct remote read/write statistics, preserved options-file behavior, correct proximal output stats, correct status propagation for schedule/wait failures, and successful checksum/table-property propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/compaction_service_job.cc -->
